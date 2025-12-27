"""OpenAI API handler with retry logic and error handling."""

import base64
import io
import os
from typing import Optional

from openai import APIError, OpenAI, RateLimitError
from PIL import Image
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from gpt_window.config.constants import DEFAULT_MAX_TOKENS, DEFAULT_MODEL
from gpt_window.config.logging_config import get_logger
from gpt_window.core.exceptions import (
    APIKeyError,
    APIResponseError,
    RateLimitError as CustomRateLimitError,
)
from gpt_window.core.utils.validators import validate_api_key

logger = get_logger(__name__)


class OpenAIHandler:
    """
    Handler for OpenAI API interactions with retry logic and error handling.

    Attributes:
        client: OpenAI client instance.
        api_key: The API key (stored temporarily in memory).
        model: The GPT model to use.
        max_tokens: Maximum tokens in API response.
    """

    def __init__(
        self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL, max_tokens: int = DEFAULT_MAX_TOKENS
    ) -> None:
        """
        Initialize the OpenAI handler.

        Args:
            api_key: OpenAI API key. If None, will try to load from environment.
            model: GPT model to use (default: gpt-4o-mini).
            max_tokens: Maximum tokens in response (default: 300).

        Raises:
            APIKeyError: If API key is invalid.
        """
        self.client: Optional[OpenAI] = None
        self.api_key: Optional[str] = None
        self.model = model
        self.max_tokens = max_tokens

        if api_key:
            self.set_api_key(api_key)
        else:
            self.load_api_key()

    def set_api_key(self, api_key: str) -> None:
        """
        Set and validate the API key.

        Args:
            api_key: The OpenAI API key.

        Raises:
            APIKeyError: If API key is invalid.
        """
        try:
            validated_key = validate_api_key(api_key)
            self.api_key = validated_key
            self.client = OpenAI(api_key=validated_key)
            logger.info("API key set successfully")
        except Exception as e:
            logger.error(f"Failed to set API key: {e}")
            raise APIKeyError(f"Invalid API key: {e}") from e

    def load_api_key(self) -> None:
        """
        Load API key from environment variable.

        Looks for OPENAI_API_KEY environment variable.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info("Loading API key from environment")
            self.set_api_key(api_key)
        else:
            logger.warning("No API key found in environment")

    def clear_api_key(self) -> None:
        """Clear the API key from memory for security."""
        self.api_key = None
        self.client = None
        logger.info("API key cleared from memory")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((RateLimitError, APIError)),
    )
    def send_request(self, image: Image.Image, query: str) -> str:
        """
        Send a vision request to OpenAI API with retry logic.

        Args:
            image: PIL Image to analyze.
            query: Text query about the image.

        Returns:
            Response text from the API.

        Raises:
            APIKeyError: If API key is not set.
            CustomRateLimitError: If rate limit is exceeded after retries.
            APIResponseError: If API returns an error.

        Example:
            >>> from PIL import Image
            >>> handler = OpenAIHandler(api_key="sk-...")
            >>> img = Image.new('RGB', (100, 100), color='blue')
            >>> response = handler.send_request(img, "What color is this?")
            >>> print(response)
            'This is a blue image.'
        """
        if not self.client:
            logger.error("Attempted API request without API key")
            raise APIKeyError("API key is not set. Please set your OpenAI API key.")

        try:
            logger.info(f"Sending API request: query='{query[:50]}...'")

            # Convert PIL Image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            logger.debug(f"Image encoded: {len(img_str)} bytes")

            # Make API request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{img_str}"},
                            },
                        ],
                    }
                ],
                max_tokens=self.max_tokens,
            )

            result = response.choices[0].message.content

            if not result:
                logger.warning("API returned empty response")
                raise APIResponseError("API returned empty response")

            logger.info(f"API request successful: {len(result)} characters")
            return result

        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise CustomRateLimitError(
                "OpenAI API rate limit exceeded. Please try again later."
            ) from e

        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIResponseError(f"OpenAI API error: {e}") from e

        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}", exc_info=True)
            raise APIResponseError(f"An unexpected error occurred: {e}") from e

    def __del__(self) -> None:
        """Clean up API key on deletion."""
        self.clear_api_key()
