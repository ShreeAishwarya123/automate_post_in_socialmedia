"""
Video Utility Functions for Social Media Automation
Handles video validation, repair, and conversion
"""

import os
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def validate_video_file(video_path: str) -> bool:
    """
    Validate if a video file is properly formatted and playable

    Args:
        video_path: Path to the video file

    Returns:
        bool: True if video is valid, False otherwise
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return False

    try:
        # Use ffprobe to check video integrity
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,width,height',
            '-of', 'csv=p=0',
            video_path
        ], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            logger.error(f"FFprobe failed for {video_path}: {result.stderr}")
            return False

        # Check if we got valid output
        output = result.stdout.strip()
        if not output:
            logger.error(f"No video stream found in {video_path}")
            return False

        logger.info(f"Video validation successful: {video_path} - {output}")
        return True

    except subprocess.TimeoutExpired:
        logger.error(f"Video validation timed out for {video_path}")
        return False
    except Exception as e:
        logger.error(f"Video validation error for {video_path}: {e}")
        return False

def repair_video_file(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Attempt to repair a corrupted video file using FFmpeg

    Args:
        input_path: Path to the corrupted video file
        output_path: Optional output path for repaired video

    Returns:
        str: Path to repaired video file, or None if repair failed
    """
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_repaired{ext}"

    try:
        logger.info(f"Attempting to repair video: {input_path} -> {output_path}")

        # Use FFmpeg to re-encode and repair the video
        # This often fixes moov atom issues and other corruption
        result = subprocess.run([
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',  # Re-encode video
            '-c:a', 'aac',      # Re-encode audio
            '-movflags', '+faststart',  # Put moov atom at beginning
            '-y',  # Overwrite output
            output_path
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        if result.returncode != 0:
            logger.error(f"Video repair failed: {result.stderr}")
            return None

        # Validate the repaired video
        if validate_video_file(output_path):
            logger.info(f"Video repair successful: {output_path}")
            return output_path
        else:
            logger.error(f"Repaired video validation failed: {output_path}")
            # Clean up failed repair
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    except subprocess.TimeoutExpired:
        logger.error(f"Video repair timed out for {input_path}")
        return None
    except Exception as e:
        logger.error(f"Video repair error for {input_path}: {e}")
        return None

def convert_video_for_platform(video_path: str, platform: str, output_dir: Optional[str] = None) -> Optional[str]:
    """
    Convert video to platform-specific requirements

    Args:
        video_path: Path to input video
        platform: Target platform (instagram, youtube, etc.)
        output_dir: Optional output directory

    Returns:
        str: Path to converted video, or None if conversion failed
    """
    if not output_dir:
        output_dir = os.path.dirname(video_path)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_{platform}.mp4")

    try:
        platform_specs = {
            'instagram': {
                'max_duration': 90,  # seconds
                'max_size': 100 * 1024 * 1024,  # 100MB
                'resolution': '1080x1920',  # 9:16 aspect ratio
            },
            'youtube': {
                'max_duration': None,  # No strict limit
                'max_size': 2 * 1024 * 1024 * 1024,  # 2GB
                'resolution': '1920x1080',  # 16:9 aspect ratio
            },
            'facebook': {
                'max_duration': 240,  # 4 minutes
                'max_size': 1024 * 1024 * 1024,  # 1GB
                'resolution': '1280x720',  # 16:9 aspect ratio
            },
            'linkedin': {
                'max_duration': 600,  # 10 minutes
                'max_size': 5 * 1024 * 1024 * 1024,  # 5GB
                'resolution': '1920x1080',  # 16:9 aspect ratio
            }
        }

        if platform not in platform_specs:
            logger.warning(f"No specifications for platform {platform}, returning original")
            return video_path

        specs = platform_specs[platform]

        # Get video info using ffprobe
        probe_result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,duration',
            '-of', 'csv=p=0:s=x',
            video_path
        ], capture_output=True, text=True)

        if probe_result.returncode != 0:
            logger.error(f"Failed to probe video {video_path}")
            return None

        # Parse video info
        try:
            width, height, duration = probe_result.stdout.strip().split('x')
            width, height = int(width), int(height)
            duration = float(duration)
        except:
            logger.error(f"Failed to parse video info for {video_path}")
            return video_path

        # Check if conversion is needed
        needs_conversion = False

        # Check duration
        if specs['max_duration'] and duration > specs['max_duration']:
            logger.info(f"Video duration {duration}s exceeds {platform} limit {specs['max_duration']}s")
            needs_conversion = True

        # Check resolution (basic aspect ratio check)
        current_aspect = width / height
        target_width, target_height = map(int, specs['resolution'].split('x'))
        target_aspect = target_width / target_height

        if abs(current_aspect - target_aspect) > 0.1:  # Allow 10% tolerance
            logger.info(f"Video aspect ratio {current_aspect:.2f} doesn't match {platform} target {target_aspect:.2f}")
            # Note: We won't force conversion for aspect ratio as it might be intentional

        if not needs_conversion:
            logger.info(f"No conversion needed for {platform}")
            return video_path

        # Perform conversion
        logger.info(f"Converting video for {platform}: {video_path} -> {output_path}")

        ffmpeg_cmd = [
            'ffmpeg',
            '-i', video_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-movflags', '+faststart'
        ]

        # Add duration limit if needed
        if specs['max_duration'] and duration > specs['max_duration']:
            ffmpeg_cmd.extend(['-t', str(specs['max_duration'])])

        # Add output path
        ffmpeg_cmd.extend(['-y', output_path])

        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            logger.error(f"Video conversion failed: {result.stderr}")
            return None

        # Validate converted video
        if validate_video_file(output_path):
            logger.info(f"Video conversion successful: {output_path}")
            return output_path
        else:
            logger.error(f"Converted video validation failed: {output_path}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    except Exception as e:
        logger.error(f"Video conversion error for {video_path}: {e}")
        return None

def ensure_video_playable(video_path: str) -> Optional[str]:
    """
    Ensure a video file is playable, repairing if necessary

    Args:
        video_path: Path to video file

    Returns:
        str: Path to playable video file, or None if unrepairable
    """
    # First, try to validate the original file
    if validate_video_file(video_path):
        return video_path

    # If validation fails, try to repair
    logger.warning(f"Video validation failed, attempting repair: {video_path}")
    repaired_path = repair_video_file(video_path)

    if repaired_path:
        return repaired_path
    else:
        logger.error(f"Video repair failed, video may be unusable: {video_path}")
        return None