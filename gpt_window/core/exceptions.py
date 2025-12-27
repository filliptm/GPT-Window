"""Custom exceptions for GPT Window."""


class GPTWindowError(Exception):
    """Base exception for all GPT Window errors."""

    pass


class APIError(GPTWindowError):
    """Base class for API-related errors."""

    pass


class APIKeyError(APIError):
    """Raised when API key is invalid or missing."""

    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    pass


class APIResponseError(APIError):
    """Raised when API returns an unexpected response."""

    pass


class ScreenshotError(GPTWindowError):
    """Raised when screenshot capture fails."""

    pass


class VideoProcessingError(GPTWindowError):
    """Base class for video processing errors."""

    pass


class VideoFileError(VideoProcessingError):
    """Raised when video file operations fail."""

    pass


class VideoCodecError(VideoProcessingError):
    """Raised when video codec errors occur."""

    pass


class ConfigurationError(GPTWindowError):
    """Raised when configuration is invalid."""

    pass


class ValidationError(GPTWindowError):
    """Raised when input validation fails."""

    pass
