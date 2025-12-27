"""PNG sequence to MP4 video compiler with enhanced error handling."""

import argparse
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from moviepy.editor import ImageSequenceClip
from PIL import Image

from gpt_window.config.constants import (
    BACKGROUND_COLOR,
    DEFAULT_FPS,
    PNG_EXTENSION,
    TARGET_SIZE,
    VIDEO_CODEC,
)
from gpt_window.config.logging_config import get_logger
from gpt_window.config.settings import Settings
from gpt_window.core.exceptions import VideoFileError, VideoProcessingError
from gpt_window.core.utils.validators import sanitize_filename, validate_directory, validate_fps

logger = get_logger(__name__)


def extract_base_name_and_number(filename: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Extract the base name and sequence number from a filename.

    Args:
        filename: Filename to parse (e.g., "animation_0001.png").

    Returns:
        Tuple of (base_name, sequence_number) or (None, None) if no match.

    Example:
        >>> extract_base_name_and_number("test_0042.png")
        ('test', 42)
    """
    match = re.search(r"(.+?)_(\d+)\.png$", filename)
    if match:
        base_name = match.group(1)
        seq_num = int(match.group(2))
        return base_name, seq_num
    return None, None


def find_max_dimensions(png_files: List[Tuple[str, int, Path]]) -> Tuple[int, int]:
    """
    Find the maximum width and height across all images in the sequence.

    Args:
        png_files: List of (base_name, seq_num, file_path) tuples.

    Returns:
        Tuple of (max_width, max_height).

    Raises:
        VideoFileError: If unable to read image dimensions.
    """
    max_width = 0
    max_height = 0

    for _, _, file_path in png_files:
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                max_width = max(max_width, width)
                max_height = max(max_height, height)
        except (OSError, IOError) as e:
            logger.warning(f"Error reading dimensions of {file_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {e}")
            raise VideoFileError(f"Failed to read image dimensions: {e}") from e

    logger.debug(f"Maximum dimensions in sequence: {max_width}x{max_height}")
    return max_width, max_height


def pad_consistently(img: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """
    Pad image to the maximum dimensions, centering the content.

    Args:
        img: PIL Image to pad.
        max_width: Target width.
        max_height: Target height.

    Returns:
        Padded PIL Image.
    """
    width, height = img.size

    # Ensure image is in RGBA format
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Create a new transparent image with the max dimensions
    new_img = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))

    # Calculate position to paste (center the original image)
    paste_x = (max_width - width) // 2
    paste_y = (max_height - height) // 2

    # Paste the original image onto the new one
    new_img.paste(img, (paste_x, paste_y), img)

    return new_img


def resize_to_target_size(img: Image.Image, target_size: int = TARGET_SIZE) -> Image.Image:
    """
    Resize image to the target size after consistent padding.

    Args:
        img: PIL Image to resize.
        target_size: Target dimension (width and height).

    Returns:
        Resized PIL Image with white background.
    """
    # Create a new white background image
    new_img = Image.new("RGBA", (target_size, target_size), BACKGROUND_COLOR)

    # Calculate the scaling factor to fit inside target_size
    width, height = img.size
    scale = min(target_size / width, target_size / height)
    new_width = int(width * scale)
    new_height = int(height * scale)

    # Resize the image
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

    # Calculate position to paste (center the resized image)
    paste_x = (target_size - new_width) // 2
    paste_y = (target_size - new_height) // 2

    # Paste the resized image onto the new one
    new_img.paste(img_resized, (paste_x, paste_y), img_resized)

    return new_img


def convert_png_sequence_to_mp4(
    png_files: List[Tuple[str, int, Path]], output_path: Path, fps: int = DEFAULT_FPS
) -> bool:
    """
    Convert a sequence of PNG files to an MP4 video.

    Args:
        png_files: List of (base_name, seq_num, file_path) tuples.
        output_path: Path to save the output MP4 file.
        fps: Frames per second for the video.

    Returns:
        True if successful, False otherwise.

    Raises:
        VideoProcessingError: If video creation fails.
    """
    # Sort files by sequence number
    png_files.sort(key=lambda x: x[1])

    # Find the maximum dimensions across all frames
    max_width, max_height = find_max_dimensions(png_files)

    # Get just the file paths
    file_paths = [item[2] for item in png_files]

    frames: List[np.ndarray] = []
    for file_path in file_paths:
        try:
            # Open image
            img = Image.open(file_path)

            # First pad consistently to max dimensions
            img = pad_consistently(img, max_width, max_height)

            # Then resize to target size if needed
            if (
                max_width > TARGET_SIZE
                or max_height > TARGET_SIZE
                or max_width < TARGET_SIZE
                or max_height < TARGET_SIZE
            ):
                img = resize_to_target_size(img, TARGET_SIZE)

            # Convert to RGB for moviepy
            img_rgb = img.convert("RGB")

            # Convert to numpy array for moviepy
            img_array = np.array(img_rgb)
            frames.append(img_array)

        except (OSError, IOError) as e:
            logger.warning(f"Error processing {file_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")
            raise VideoProcessingError(f"Failed to process frame: {e}") from e

    if not frames:
        logger.error(f"No valid frames to create video for {output_path}")
        return False

    try:
        # Create video clip
        logger.info(f"Creating video with {len(frames)} frames at {fps} FPS")
        clip = ImageSequenceClip(frames, fps=fps)

        # Write to file
        clip.write_videofile(str(output_path), codec=VIDEO_CODEC, logger=None)

        logger.info(f"Created video: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating video {output_path}: {e}")
        raise VideoProcessingError(f"Failed to create video: {e}") from e


def process_directory(directory: Path, output_dir: Path, fps: int) -> int:
    """
    Process a directory of PNG files and create MP4 videos.

    Args:
        directory: Directory containing PNG files.
        output_dir: Directory to save output videos.
        fps: Frames per second for videos.

    Returns:
        Number of successfully processed sequences.
    """
    # Dictionary to group files by base name
    sequences: Dict[str, List[Tuple[str, int, Path]]] = defaultdict(list)

    # Get PNG files from the directory (not recursive)
    logger.info(f"Scanning directory: {directory}")
    for file in os.listdir(directory):
        if file.lower().endswith(PNG_EXTENSION):
            full_path = directory / file
            base_name, seq_num = extract_base_name_and_number(file)

            if base_name and seq_num is not None:
                sequences[base_name].append((base_name, seq_num, full_path))

    if not sequences:
        logger.warning(f"No PNG sequences found in {directory}")
        return 0

    # Get directory name for use in output file name
    dir_name = directory.name

    # Count successfully processed sequences
    successful_sequences = 0

    # Process each sequence
    for base_name, png_files in sequences.items():
        if len(png_files) > 0:
            logger.info(f"Processing sequence '{base_name}' with {len(png_files)} frames")

            # Create output filename based on directory name and base name
            output_filename = sanitize_filename(f"{dir_name}_{base_name}.mp4")
            output_file = output_dir / output_filename

            try:
                success = convert_png_sequence_to_mp4(png_files, output_file, fps)
                if success:
                    successful_sequences += 1
            except VideoProcessingError as e:
                logger.error(f"Failed to process sequence {base_name}: {e}")
                continue

    return successful_sequences


def main() -> None:
    """Main entry point for the PNG to MP4 compiler."""
    settings = Settings.from_env()

    parser = argparse.ArgumentParser(description="Convert PNG sequences to MP4 videos")
    parser.add_argument(
        "input_dir",
        nargs="?",
        help="Directory containing subdirectories of PNG files",
        default=str(settings.input_dir),
    )
    parser.add_argument(
        "--output_dir",
        help="Directory to save MP4 files",
        default=str(settings.output_dir),
    )
    parser.add_argument(
        "--fps", type=int, help="Frames per second for the videos", default=settings.video_fps
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process main directory and all subdirectories",
    )
    args = parser.parse_args()

    # Setup logging
    logger = get_logger(__name__)
    logger.info("PNG to MP4 Compiler starting")

    try:
        # Validate inputs
        input_dir = validate_directory(args.input_dir)
        fps = validate_fps(args.fps)
        output_dir = Path(args.output_dir)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Directory processing counter
        processed_dirs = 0

        if args.recursive:
            # Process the main directory
            count = process_directory(input_dir, output_dir, fps)
            if count > 0:
                processed_dirs += 1

            # Process each subdirectory
            for subdir in input_dir.iterdir():
                if subdir.is_dir():
                    count = process_directory(subdir, output_dir, fps)
                    if count > 0:
                        processed_dirs += 1
        else:
            # Process only the subdirectories, not the main directory
            for subdir in input_dir.iterdir():
                if subdir.is_dir():
                    count = process_directory(subdir, output_dir, fps)
                    if count > 0:
                        processed_dirs += 1

        if processed_dirs > 0:
            logger.info(
                f"Processing complete. Processed {processed_dirs} directories. "
                f"Videos saved to {output_dir}"
            )
        else:
            logger.warning("No PNG sequences found in the specified directories.")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return


if __name__ == "__main__":
    main()
