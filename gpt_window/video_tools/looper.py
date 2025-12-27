"""Video looping tool with proper error handling and cleanup."""

import argparse
import os
import tempfile
from pathlib import Path
from typing import List

from moviepy.editor import VideoFileClip, concatenate_videoclips

from gpt_window.config.constants import AUDIO_CODEC, MP4_EXTENSION, VIDEO_CODEC, VIDEO_PRESET
from gpt_window.config.logging_config import get_logger
from gpt_window.config.settings import Settings
from gpt_window.core.exceptions import VideoFileError, VideoProcessingError
from gpt_window.core.utils.validators import validate_directory, validate_positive_int

logger = get_logger(__name__)

DEFAULT_LOOP_COUNT = 3


def loop_video(video_path: Path, loop_count: int) -> bool:
    """
    Loop a video file the specified number of times and replace the original.

    Args:
        video_path: Path to the video file.
        loop_count: Number of times to loop the video.

    Returns:
        True if successful, False otherwise.

    Raises:
        VideoFileError: If video file operations fail.
        VideoProcessingError: If video processing fails.
    """
    logger.info(f"Processing: {video_path}")

    # Create a temporary file in the same directory
    temp_fd, temp_path = tempfile.mkstemp(suffix=MP4_EXTENSION, dir=video_path.parent)
    temp_path_obj = Path(temp_path)

    try:
        # Close the file descriptor as moviepy will handle the file
        os.close(temp_fd)

        # Load the video clip
        logger.debug(f"Loading video: {video_path}")
        clip = VideoFileClip(str(video_path))

        # Create a list with the clip repeated loop_count times
        clips = [clip] * loop_count
        logger.debug(f"Looping video {loop_count} times")

        # Concatenate the clips
        final_clip = concatenate_videoclips(clips)

        # Write the result to the temporary file
        logger.debug(f"Writing looped video to: {temp_path_obj}")
        final_clip.write_videofile(
            str(temp_path_obj),
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            preset=VIDEO_PRESET,
            threads=4,
            logger=None,
        )

        # Close the clips to release resources
        final_clip.close()
        clip.close()

        # Replace the original file with the new looped version
        logger.debug(f"Replacing original file: {video_path}")
        os.replace(temp_path_obj, video_path)

        logger.info(f"Successfully looped and replaced: {video_path}")
        return True

    except OSError as e:
        logger.error(f"File operation error for {video_path}: {e}")
        raise VideoFileError(f"Failed to process video file: {e}") from e

    except Exception as e:
        logger.error(f"Error processing {video_path}: {e}")
        raise VideoProcessingError(f"Failed to loop video: {e}") from e

    finally:
        # Clean up temp file if it still exists
        if temp_path_obj.exists():
            try:
                temp_path_obj.unlink()
                logger.debug(f"Cleaned up temp file: {temp_path_obj}")
            except OSError as e:
                logger.warning(f"Failed to clean up temp file {temp_path_obj}: {e}")


def process_videos(
    input_folder: Path, loop_count: int, include_subfolders: bool = False
) -> tuple[int, int]:
    """
    Process all MP4 files in a folder.

    Args:
        input_folder: Folder containing MP4 files.
        loop_count: Number of times to loop each video.
        include_subfolders: Whether to process subfolders recursively.

    Returns:
        Tuple of (success_count, total_count).
    """
    # Find all MP4 files
    mp4_files: List[Path]
    if include_subfolders:
        mp4_files = list(input_folder.glob(f"**/*{MP4_EXTENSION}"))
    else:
        mp4_files = list(input_folder.glob(f"*{MP4_EXTENSION}"))

    if not mp4_files:
        logger.warning(f"No {MP4_EXTENSION} files found in {input_folder}")
        return 0, 0

    logger.info(f"Found {len(mp4_files)} {MP4_EXTENSION} files to process")

    # Process each file
    success_count = 0
    for file_path in mp4_files:
        try:
            if loop_video(file_path, loop_count):
                success_count += 1
        except (VideoFileError, VideoProcessingError) as e:
            logger.error(f"Failed to process {file_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}", exc_info=True)
            continue

    return success_count, len(mp4_files)


def main() -> None:
    """Main entry point for the video looper."""
    settings = Settings.from_env()

    parser = argparse.ArgumentParser(description="Loop videos a specified number of times")
    parser.add_argument(
        "input_folder",
        nargs="?",
        help="Folder containing MP4 files",
        default=str(settings.input_dir),
    )
    parser.add_argument(
        "--loop_count",
        type=int,
        help="Number of times to loop each video",
        default=DEFAULT_LOOP_COUNT,
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subfolders recursively",
    )
    args = parser.parse_args()

    # Setup logging
    logger = get_logger(__name__)
    logger.info("Video Looper starting")

    try:
        # Validate inputs
        input_folder = validate_directory(args.input_folder)
        loop_count = validate_positive_int(args.loop_count, "loop_count")

        logger.info(f"Input folder: {input_folder}")
        logger.info(f"Loop count: {loop_count}")
        logger.info(f"Recursive: {args.recursive}")

        # Process videos
        success_count, total_count = process_videos(input_folder, loop_count, args.recursive)

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
