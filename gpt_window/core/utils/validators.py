"""Input validation utilities for GPT Window."""

import re
from pathlib import Path
from typing import Union

from PyQt5.QtCore import QRect

from gpt_window.config.constants import MAX_FPS, MIN_FPS
from gpt_window.core.exceptions import ValidationError


def validate_api_key(api_key: str) -> str:
    """
    Validate OpenAI API key format.

    Args:
        api_key: The API key to validate.

    Returns:
        The validated API key.

    Raises:
        ValidationError: If API key is invalid.

    Example:
        >>> validate_api_key("sk-proj-1234567890")
        'sk-proj-1234567890'
    """
    if not api_key:
        raise ValidationError("API key cannot be empty")

    if not isinstance(api_key, str):
        raise ValidationError("API key must be a string")

    # OpenAI API keys start with 'sk-'
    if not api_key.startswith("sk-"):
        raise ValidationError("Invalid API key format (must start with 'sk-')")

    # Check minimum length (OpenAI keys are typically 40+ characters)
    if len(api_key) < 20:
        raise ValidationError("API key is too short")

    return api_key


def validate_geometry(geometry: QRect) -> QRect:
    """
    Validate screenshot geometry bounds.

    Args:
        geometry: QRect defining the screenshot region.

    Returns:
        The validated geometry.

    Raises:
        ValidationError: If geometry is invalid.

    Example:
        >>> from PyQt5.QtCore import QRect
        >>> rect = QRect(0, 0, 100, 100)
        >>> validate_geometry(rect)
        PyQt5.QtCore.QRect(0, 0, 100, 100)
    """
    if not isinstance(geometry, QRect):
        raise ValidationError("Geometry must be a QRect instance")

    if geometry.width() <= 0:
        raise ValidationError(f"Invalid geometry width: {geometry.width()}")

    if geometry.height() <= 0:
        raise ValidationError(f"Invalid geometry height: {geometry.height()}")

    if geometry.left() < 0 or geometry.top() < 0:
        raise ValidationError("Geometry position cannot be negative")

    # Check for reasonable bounds (not larger than typical screen sizes)
    max_dimension = 10000
    if geometry.width() > max_dimension or geometry.height() > max_dimension:
        raise ValidationError(
            f"Geometry dimensions too large (max: {max_dimension}x{max_dimension})"
        )

    return geometry


def validate_fps(fps: int) -> int:
    """
    Validate frames per second value.

    Args:
        fps: Frames per second value.

    Returns:
        The validated FPS value.

    Raises:
        ValidationError: If FPS is out of valid range.

    Example:
        >>> validate_fps(30)
        30
        >>> validate_fps(0)
        Traceback (most recent call last):
        ...
        ValidationError: FPS must be between 1 and 120, got 0
    """
    if not isinstance(fps, int):
        raise ValidationError(f"FPS must be an integer, got {type(fps).__name__}")

    if fps < MIN_FPS or fps > MAX_FPS:
        raise ValidationError(f"FPS must be between {MIN_FPS} and {MAX_FPS}, got {fps}")

    return fps


def validate_directory(path: Union[str, Path]) -> Path:
    """
    Validate that a directory exists and is readable.

    Args:
        path: Path to the directory.

    Returns:
        Validated Path object.

    Raises:
        ValidationError: If directory doesn't exist or isn't a directory.

    Example:
        >>> from pathlib import Path
        >>> validate_directory("/tmp")
        PosixPath('/tmp')
    """
    path_obj = Path(path) if isinstance(path, str) else path

    if not path_obj.exists():
        raise ValidationError(f"Directory does not exist: {path_obj}")

    if not path_obj.is_dir():
        raise ValidationError(f"Path is not a directory: {path_obj}")

    # Check if directory is readable
    if not path_obj.stat().st_mode & 0o444:
        raise ValidationError(f"Directory is not readable: {path_obj}")

    return path_obj


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent path traversal and special character issues.

    Args:
        filename: The filename to sanitize.
        max_length: Maximum allowed filename length.

    Returns:
        Sanitized filename.

    Raises:
        ValidationError: If filename is empty after sanitization.

    Example:
        >>> sanitize_filename("../../etc/passwd")
        'etcpasswd'
        >>> sanitize_filename("my file (copy).txt")
        'my_file_copy.txt'
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")

    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")

    # Remove or replace dangerous characters
    # Keep alphanumeric, dots, dashes, underscores
    filename = re.sub(r'[^\w\-.]', '_', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Limit length
    if len(filename) > max_length:
        # Keep extension if present
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            max_name_length = max_length - len(ext) - 1
            filename = f"{name[:max_name_length]}.{ext}"
        else:
            filename = filename[:max_length]

    if not filename:
        raise ValidationError("Filename is empty after sanitization")

    return filename


def validate_positive_int(value: int, name: str) -> int:
    """
    Validate that a value is a positive integer.

    Args:
        value: The value to validate.
        name: Name of the parameter (for error messages).

    Returns:
        The validated value.

    Raises:
        ValidationError: If value is not a positive integer.

    Example:
        >>> validate_positive_int(10, "count")
        10
        >>> validate_positive_int(-5, "count")
        Traceback (most recent call last):
        ...
        ValidationError: count must be positive, got -5
    """
    if not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer, got {type(value).__name__}")

    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")

    return value
