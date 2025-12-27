"""Screenshot capture utilities for GPT Window."""

from typing import Optional

import mss
from PIL import Image
from PyQt5.QtCore import QRect

from gpt_window.config.logging_config import get_logger
from gpt_window.core.exceptions import ScreenshotError
from gpt_window.core.utils.validators import validate_geometry

logger = get_logger(__name__)


def capture_screenshot(geometry: QRect) -> Optional[Image.Image]:
    """
    Capture a screenshot of the specified screen region.

    Args:
        geometry: QRect defining the screen region to capture.

    Returns:
        PIL Image of the captured region, or None if capture fails.

    Raises:
        ScreenshotError: If screenshot capture fails critically.

    Example:
        >>> from PyQt5.QtCore import QRect
        >>> rect = QRect(0, 0, 100, 100)
        >>> img = capture_screenshot(rect)
        >>> if img:
        ...     img.save("screenshot.png")
    """
    try:
        # Validate geometry
        geometry = validate_geometry(geometry)

        logger.debug(
            f"Capturing screenshot: x={geometry.left()}, y={geometry.top()}, "
            f"w={geometry.width()}, h={geometry.height()}"
        )

        with mss.mss() as sct:
            monitor = {
                "top": geometry.top(),
                "left": geometry.left(),
                "width": geometry.width(),
                "height": geometry.height(),
            }

            # Capture the screen region
            sct_img = sct.grab(monitor)

            # Convert to PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            logger.info(f"Screenshot captured successfully: {img.size}")
            return img

    except mss.exception.ScreenShotError as e:
        logger.error(f"MSS screenshot error: {e}")
        raise ScreenshotError(f"Failed to capture screenshot: {e}") from e

    except OSError as e:
        logger.error(f"OS error during screenshot: {e}")
        raise ScreenshotError(f"OS error during screenshot capture: {e}") from e

    except ValueError as e:
        logger.error(f"Invalid geometry for screenshot: {e}")
        raise ScreenshotError(f"Invalid screenshot geometry: {e}") from e

    except Exception as e:
        logger.error(f"Unexpected error capturing screenshot: {e}", exc_info=True)
        # Don't raise for unexpected errors, just return None
        # This prevents the app from crashing on screenshot issues
        return None
