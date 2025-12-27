"""Pytest fixtures for GPT Window tests."""

import pytest
from PIL import Image
from PyQt5.QtCore import QRect
from unittest.mock import MagicMock, Mock


@pytest.fixture
def mock_image():
    """Create a test PIL Image."""
    return Image.new("RGB", (100, 100), color="blue")


@pytest.fixture
def mock_large_image():
    """Create a larger test PIL Image."""
    return Image.new("RGB", (800, 600), color="red")


@pytest.fixture
def mock_geometry():
    """Create a mock QRect geometry."""
    return QRect(0, 0, 100, 100)


@pytest.fixture
def mock_large_geometry():
    """Create a larger mock QRect geometry."""
    return QRect(0, 0, 800, 600)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_choice = Mock()
    mock_choice.message.content = "This is a test response from the API."

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    return mock_response


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_openai_response
    return mock_client


@pytest.fixture
def valid_api_key():
    """Return a valid-looking API key for testing."""
    return "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def invalid_api_keys():
    """Return a list of invalid API keys for testing."""
    return [
        "",  # Empty
        "invalid",  # Wrong format
        "sk-",  # Too short
        "not-an-api-key",  # Wrong prefix
        12345,  # Not a string
    ]
