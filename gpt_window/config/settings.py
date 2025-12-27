"""Settings and configuration management for GPT Window."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .constants import (
    DEFAULT_FPS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    MAX_DIMENSION,
    TARGET_SIZE,
    VIDEO_CODEC,
)


@dataclass
class Settings:
    """Application settings loaded from environment variables or defaults."""

    # API Settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS

    # Video Settings
    video_fps: int = DEFAULT_FPS
    target_size: int = TARGET_SIZE
    max_dimension: int = MAX_DIMENSION
    video_codec: str = VIDEO_CODEC

    # Paths
    input_dir: Path = field(default_factory=lambda: Path("./input"))
    output_dir: Path = field(default_factory=lambda: Path("./output"))

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create Settings from environment variables.

        Environment variables:
            OPENAI_API_KEY: OpenAI API key
            GPT_WINDOW_INPUT_DIR: Input directory for video processing
            GPT_WINDOW_OUTPUT_DIR: Output directory for video processing
            GPT_WINDOW_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
            GPT_WINDOW_LOG_FILE: Path to log file

        Returns:
            Settings instance with values from environment or defaults.
        """
        input_dir = os.getenv("GPT_WINDOW_INPUT_DIR", "./input")
        output_dir = os.getenv("GPT_WINDOW_OUTPUT_DIR", "./output")
        log_level = os.getenv("GPT_WINDOW_LOG_LEVEL", "INFO")
        log_file_str = os.getenv("GPT_WINDOW_LOG_FILE")

        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            input_dir=Path(input_dir),
            output_dir=Path(output_dir),
            log_level=log_level,
            log_file=Path(log_file_str) if log_file_str else None,
        )

    def ensure_directories(self) -> None:
        """Create input and output directories if they don't exist."""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
