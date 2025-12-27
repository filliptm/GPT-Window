"""Tests for validation utilities."""

import pytest
from pathlib import Path
from PyQt5.QtCore import QRect

from gpt_window.core.utils.validators import (
    validate_api_key,
    validate_geometry,
    validate_fps,
    validate_positive_int,
    sanitize_filename,
)
from gpt_window.core.exceptions import ValidationError


class TestValidateAPIKey:
    """Tests for API key validation."""

    def test_valid_api_key(self, valid_api_key):
        """Test validation passes for valid API key."""
        result = validate_api_key(valid_api_key)
        assert result == valid_api_key

    def test_empty_api_key(self):
        """Test validation fails for empty API key."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_api_key("")

    def test_wrong_prefix(self):
        """Test validation fails for wrong prefix."""
        with pytest.raises(ValidationError, match="must start with 'sk-'"):
            validate_api_key("invalid-key-format")

    def test_too_short(self):
        """Test validation fails for too short API key."""
        with pytest.raises(ValidationError, match="too short"):
            validate_api_key("sk-short")

    def test_non_string(self):
        """Test validation fails for non-string input."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_api_key(12345)  # type: ignore


class TestValidateGeometry:
    """Tests for geometry validation."""

    def test_valid_geometry(self, mock_geometry):
        """Test validation passes for valid geometry."""
        result = validate_geometry(mock_geometry)
        assert result == mock_geometry

    def test_zero_width(self):
        """Test validation fails for zero width."""
        rect = QRect(0, 0, 0, 100)
        with pytest.raises(ValidationError, match="Invalid geometry width"):
            validate_geometry(rect)

    def test_zero_height(self):
        """Test validation fails for zero height."""
        rect = QRect(0, 0, 100, 0)
        with pytest.raises(ValidationError, match="Invalid geometry height"):
            validate_geometry(rect)

    def test_negative_position(self):
        """Test validation fails for negative position."""
        rect = QRect(-10, -10, 100, 100)
        with pytest.raises(ValidationError, match="cannot be negative"):
            validate_geometry(rect)

    def test_too_large(self):
        """Test validation fails for unreasonably large dimensions."""
        rect = QRect(0, 0, 20000, 20000)
        with pytest.raises(ValidationError, match="too large"):
            validate_geometry(rect)


class TestValidateFPS:
    """Tests for FPS validation."""

    def test_valid_fps(self):
        """Test validation passes for valid FPS values."""
        assert validate_fps(24) == 24
        assert validate_fps(30) == 30
        assert validate_fps(60) == 60

    def test_fps_too_low(self):
        """Test validation fails for FPS below minimum."""
        with pytest.raises(ValidationError, match="must be between 1 and 120"):
            validate_fps(0)

    def test_fps_too_high(self):
        """Test validation fails for FPS above maximum."""
        with pytest.raises(ValidationError, match="must be between 1 and 120"):
            validate_fps(121)

    def test_non_integer_fps(self):
        """Test validation fails for non-integer FPS."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_fps(30.5)  # type: ignore


class TestValidatePositiveInt:
    """Tests for positive integer validation."""

    def test_valid_positive_int(self):
        """Test validation passes for positive integers."""
        assert validate_positive_int(1, "test") == 1
        assert validate_positive_int(100, "test") == 100

    def test_zero(self):
        """Test validation fails for zero."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_int(0, "count")

    def test_negative(self):
        """Test validation fails for negative values."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_int(-5, "count")

    def test_non_integer(self):
        """Test validation fails for non-integer."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_int(10.5, "count")  # type: ignore


class TestSanitizeFilename:
    """Tests for filename sanitization."""

    def test_normal_filename(self):
        """Test normal filename passes through."""
        assert sanitize_filename("test.txt") == "test.txt"
        assert sanitize_filename("my_file-123.mp4") == "my_file-123.mp4"

    def test_path_traversal(self):
        """Test path traversal is removed."""
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_special_characters(self):
        """Test special characters are replaced."""
        result = sanitize_filename("my file (copy).txt")
        assert result == "my_file_copy.txt"

    def test_empty_after_sanitization(self):
        """Test error is raised if filename is empty after sanitization."""
        with pytest.raises(ValidationError, match="empty after sanitization"):
            sanitize_filename("../../")

    def test_length_limit(self):
        """Test filename is truncated if too long."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name, max_length=255)
        assert len(result) <= 255
        assert result.endswith(".txt")
