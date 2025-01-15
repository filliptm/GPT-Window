import os
from openai import OpenAI
from PIL import Image
import io
import base64

class APIHandler:
    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = "gpt-4-vision-preview"  # Use the correct model for vision tasks

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def save_api_key(self):
        # For security reasons, we won't save the API key to a file
        # Instead, we'll keep it in memory for the duration of the session
        pass

    def load_api_key(self):
        # Try to load from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.set_api_key(api_key)

    def send_request(self, image, query):
        if not self.client:
            raise ValueError("API key is not set")

        # Convert PIL Image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You follow the instructions to a T. You dont reply with anything else except for what is asked of you. When asked to write code you write full production code with no further explenations or filler."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": query
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_str}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {str(e)}"
