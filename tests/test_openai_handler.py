"""Tests for OpenAI API handler."""

import pytest
from unittest.mock import Mock, patch

from gpt_window.core.api.openai_handler import OpenAIHandler
from gpt_window.core.exceptions import APIKeyError, APIResponseError


class TestOpenAIHandler:
    """Tests for OpenAIHandler class."""

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        handler = OpenAIHandler()
        assert handler.client is None
        assert handler.api_key is None

    def test_init_with_valid_api_key(self, valid_api_key):
        """Test initialization with valid API key."""
        handler = OpenAIHandler(api_key=valid_api_key)
        assert handler.client is not None
        assert handler.api_key == valid_api_key

    def test_init_with_invalid_api_key(self):
        """Test initialization with invalid API key raises error."""
        with pytest.raises(APIKeyError):
            OpenAIHandler(api_key="invalid")

    def test_set_api_key_valid(self, valid_api_key):
        """Test setting a valid API key."""
        handler = OpenAIHandler()
        handler.set_api_key(valid_api_key)
        assert handler.client is not None
        assert handler.api_key == valid_api_key

    def test_set_api_key_invalid(self):
        """Test setting an invalid API key raises error."""
        handler = OpenAIHandler()
        with pytest.raises(APIKeyError):
            handler.set_api_key("invalid")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz"})
    def test_load_api_key_from_env(self):
        """Test loading API key from environment."""
        handler = OpenAIHandler()
        handler.load_api_key()
        assert handler.api_key is not None
        assert handler.client is not None

    def test_clear_api_key(self, valid_api_key):
        """Test clearing API key from memory."""
        handler = OpenAIHandler(api_key=valid_api_key)
        assert handler.api_key is not None

        handler.clear_api_key()
        assert handler.api_key is None
        assert handler.client is None

    def test_send_request_without_api_key(self, mock_image):
        """Test sending request without API key raises error."""
        handler = OpenAIHandler()
        with pytest.raises(APIKeyError, match="API key is not set"):
            handler.send_request(mock_image, "test query")

    @patch("gpt_window.core.api.openai_handler.OpenAI")
    def test_send_request_success(self, mock_openai_class, valid_api_key, mock_image, mock_openai_response):
        """Test successful API request."""
        # Setup mock
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client

        # Create handler and send request
        handler = OpenAIHandler(api_key=valid_api_key)
        result = handler.send_request(mock_image, "What is this?")

        # Verify
        assert result == "This is a test response from the API."
        mock_client.chat.completions.create.assert_called_once()

    @patch("gpt_window.core.api.openai_handler.OpenAI")
    def test_send_request_empty_response(self, mock_openai_class, valid_api_key, mock_image):
        """Test handling of empty API response."""
        # Setup mock with empty response
        mock_choice = Mock()
        mock_choice.message.content = None

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        # Create handler and send request
        handler = OpenAIHandler(api_key=valid_api_key)

        with pytest.raises(APIResponseError, match="empty response"):
            handler.send_request(mock_image, "test")
