"""Video processing tool for resizing and limiting frames."""

import argparse
import tempfile
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np

from gpt_window.config.constants import MAX_DIMENSION, MAX_FRAMES
from gpt_window.config.logging_config import get_logger
from gpt_window.config.settings import Settings
from gpt_window.core.exceptions import VideoFileError, VideoProcessingError
from gpt_window.core.utils.validators import validate_directory, validate_positive_int

logger = get_logger(__name__)


def resize_frame(frame: np.ndarray, max_dimension: int = MAX_DIMENSION) -> np.ndarray:
    """
    Resize frame maintaining aspect ratio with max dimension.

    Args:
        frame: Input frame as numpy array.
        max_dimension: Maximum dimension (width or height) in pixels.

    Returns:
        Resized frame.
    """
    height, width = frame.shape[:2]

    # If already smaller than max dimension, return original
    if width <= max_dimension and height <= max_dimension:
        return frame

    # Calculate new dimensions
    if width > height:
        new_width = max_dimension
        new_height = int(height * (max_dimension / width))
    else:
        new_height = max_dimension
        new_width = int(width * (max_dimension / height))

    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)


def process_video(
    video_path: Path, max_dimension: int = MAX_DIMENSION, max_frames: int = MAX_FRAMES
) -> bool:
    """
    Process a video file to limit frames and resize.

    Args:
        video_path: Path to the video file.
        max_dimension: Maximum dimension for resizing.
        max_frames: Maximum number of frames to keep.

    Returns:
        True if successful, False otherwise.

    Raises:
        VideoFileError: If video file operations fail.
        VideoProcessingError: If video processing fails.
    """
    logger.info(f"Processing: {video_path}")

    # Open video file
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.error(f"Failed to open video file: {video_path}")
        raise VideoFileError(f"Cannot open video file: {video_path}")

    try:
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.debug(f"Original: {frame_count} frames at {fps} FPS")

        # Create temporary output file
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4", dir=video_path.parent)
        temp_path_obj = Path(temp_path)

        try:
            # Get first frame to determine dimensions after resize
            ret, frame = cap.read()
            if not ret:
                logger.error(f"Failed to read first frame from: {video_path}")
                raise VideoProcessingError("Cannot read video frames")

            resized_frame = resize_frame(frame, max_dimension)
            height, width = resized_frame.shape[:2]

            logger.debug(f"New dimensions: {width}x{height}")

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(temp_path_obj), fourcc, fps, (width, height))

            if not out.isOpened():
                raise VideoProcessingError("Failed to create video writer")

            # Process frames
            frame_limit = min(frame_count, max_frames)
            frames_processed = 1  # Count first frame
            out.write(resized_frame)

            while frames_processed < frame_limit:
                ret, frame = cap.read()
                if not ret:
                    break

                resized_frame = resize_frame(frame, max_dimension)
                out.write(resized_frame)
                frames_processed += 1

            logger.debug(f"Processed {frames_processed} frames")

            # Release resources
            cap.release()
            out.release()

            # Replace original file with processed file
            import os

            os.replace(temp_path_obj, video_path)
            logger.info(f"Completed processing: {video_path}")
            return True

        except Exception as e:
            # Clean up temp file on error
            if temp_path_obj.exists():
                temp_path_obj.unlink()
            raise

    except cv2.error as e:
        logger.error(f"OpenCV error processing {video_path}: {e}")
        raise VideoProcessingError(f"OpenCV error: {e}") from e

    except OSError as e:
        logger.error(f"File operation error for {video_path}: {e}")
        raise VideoFileError(f"File operation failed: {e}") from e

    finally:
        cap.release()


def process_all_videos(
    target_dir: Path, max_dimension: int = MAX_DIMENSION, max_frames: int = MAX_FRAMES
) -> Tuple[int, int]:
    """
    Process all MP4 files in a directory and its subdirectories.

    Args:
        target_dir: Directory containing videos.
        max_dimension: Maximum dimension for resizing.
        max_frames: Maximum number of frames to keep.

    Returns:
        Tuple of (success_count, total_count).
    """
    # Find all MP4 files in target directory and subdirectories
    mp4_files = list(target_dir.rglob("*.mp4"))

    if not mp4_files:
        logger.warning(f"No MP4 files found in {target_dir}")
        return 0, 0

    logger.info(f"Found {len(mp4_files)} MP4 files to process")

    success_count = 0
    for video_path in mp4_files:
        try:
            if process_video(video_path, max_dimension, max_frames):
                success_count += 1
        except (VideoFileError, VideoProcessingError) as e:
            logger.error(f"Failed to process {video_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing {video_path}: {e}", exc_info=True)
            continue

    return success_count, len(mp4_files)


def main() -> None:
    """Main entry point for the video processor."""
    settings = Settings.from_env()

    parser = argparse.ArgumentParser(
        description="Process videos: resize and limit frame count"
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        help="Directory containing MP4 files",
        default=str(settings.input_dir),
    )
    parser.add_argument(
        "--max_dimension",
        type=int,
        help="Maximum dimension (width or height) in pixels",
        default=MAX_DIMENSION,
    )
    parser.add_argument(
        "--max_frames",
        type=int,
        help="Maximum number of frames to keep",
        default=MAX_FRAMES,
    )
    args = parser.parse_args()

    # Setup logging
    logger = get_logger(__name__)
    logger.info("Video Processor starting")

    try:
        # Validate inputs
        target_dir = validate_directory(args.target_dir)
        max_dimension = validate_positive_int(args.max_dimension, "max_dimension")
        max_frames = validate_positive_int(args.max_frames, "max_frames")

        logger.info(f"Processing videos in: {target_dir}")
        logger.info(f"Max dimension: {max_dimension}px")
        logger.info(f"Max frames: {max_frames}")

        # Process all videos
        success_count, total_count = process_all_videos(target_dir, max_dimension, max_frames)

        # Report results
        logger.info(f"Processing complete: {success_count}/{total_count} files successfully processed")

        if success_count == 0 and total_count > 0:
            logger.error("All video processing failed")
        elif success_count < total_count:
            logger.warning(f"{total_count - success_count} files failed to process")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return


if __name__ == "__main__":
    main()
