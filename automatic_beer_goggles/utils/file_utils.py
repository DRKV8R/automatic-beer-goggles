"""
Utility functions for file validation and processing.
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Tuple, Union
from loguru import logger


def validate_audio_file(file_path: Union[str, Path]) -> bool:
    """
    Validate that a file is a supported audio format.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if valid audio file, False otherwise
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    # Check file extension
    supported_audio_extensions = {'.wav', '.mp3', '.flac', '.aac', '.m4a', '.ogg'}
    if file_path.suffix.lower() not in supported_audio_extensions:
        logger.error(f"Unsupported audio format: {file_path.suffix}")
        return False
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and not mime_type.startswith('audio/'):
        logger.error(f"Invalid MIME type for audio file: {mime_type}")
        return False
    
    # Check file size (minimum 1KB)
    if file_path.stat().st_size < 1024:
        logger.error(f"Audio file too small: {file_path}")
        return False
    
    return True


def validate_image_file(file_path: Union[str, Path]) -> bool:
    """
    Validate that a file is a supported image format.
    
    Args:
        file_path: Path to image file
        
    Returns:
        True if valid image file, False otherwise
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    # Check file extension
    supported_image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    if file_path.suffix.lower() not in supported_image_extensions:
        logger.error(f"Unsupported image format: {file_path.suffix}")
        return False
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and not mime_type.startswith('image/'):
        logger.error(f"Invalid MIME type for image file: {mime_type}")
        return False
    
    # Check file size (minimum 1KB)
    if file_path.stat().st_size < 1024:
        logger.error(f"Image file too small: {file_path}")
        return False
    
    return True


def find_audio_files(directory: Union[str, Path], 
                    patterns: List[str] = None) -> List[Path]:
    """
    Find all audio files in a directory matching given patterns.
    
    Args:
        directory: Directory to search
        patterns: List of glob patterns (default: ['*.wav', '*.mp3', '*.flac'])
        
    Returns:
        List of valid audio file paths
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory not found or not a directory: {directory}")
        return []
    
    if patterns is None:
        patterns = ['*.wav', '*.mp3', '*.flac', '*.aac', '*.m4a', '*.ogg']
    
    audio_files = []
    for pattern in patterns:
        found_files = list(directory.glob(pattern))
        audio_files.extend(found_files)
    
    # Validate and filter files
    valid_files = []
    for file_path in audio_files:
        if validate_audio_file(file_path):
            valid_files.append(file_path)
    
    logger.info(f"Found {len(valid_files)} valid audio files in {directory}")
    return valid_files


def find_image_files(directory: Union[str, Path], 
                    patterns: List[str] = None) -> List[Path]:
    """
    Find all image files in a directory matching given patterns.
    
    Args:
        directory: Directory to search
        patterns: List of glob patterns (default: ['*.png', '*.jpg', '*.jpeg'])
        
    Returns:
        List of valid image file paths
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory not found or not a directory: {directory}")
        return []
    
    if patterns is None:
        patterns = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff', '*.tif']
    
    image_files = []
    for pattern in patterns:
        found_files = list(directory.glob(pattern))
        image_files.extend(found_files)
    
    # Validate and filter files
    valid_files = []
    for file_path in image_files:
        if validate_image_file(file_path):
            valid_files.append(file_path)
    
    logger.info(f"Found {len(valid_files)} valid image files in {directory}")
    return valid_files


def calculate_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Calculate file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return 0.0
    
    return file_path.stat().st_size / (1024 * 1024)


def ensure_directory_exists(directory: Union[str, Path], create: bool = True) -> bool:
    """
    Ensure a directory exists, optionally creating it.
    
    Args:
        directory: Directory path
        create: Whether to create the directory if it doesn't exist
        
    Returns:
        True if directory exists (or was created), False otherwise
    """
    directory = Path(directory)
    
    if directory.exists():
        return directory.is_dir()
    
    if create:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
    
    return False


def clean_filename(filename: str) -> str:
    """
    Clean a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename safe for filesystem
    """
    import re
    
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '_', filename)
    
    # Remove multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores and dots
    cleaned = cleaned.strip('_.')
    
    # Ensure filename is not empty
    if not cleaned:
        cleaned = "untitled"
    
    return cleaned


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2:30" or "1:15:30")
    """
    if seconds < 0:
        return "0:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.2 MB", "450 KB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_system_info() -> dict:
    """
    Get basic system information for diagnostics.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import psutil
    
    try:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
        }
    except Exception as e:
        logger.warning(f"Could not gather system info: {e}")
        return {"error": str(e)}


def check_dependencies() -> dict:
    """
    Check if required external dependencies are available.
    
    Returns:
        Dictionary with dependency status
    """
    import subprocess
    import shutil
    
    dependencies = {
        "ffmpeg": False,
        "ffprobe": False,
    }
    
    # Check FFmpeg
    if shutil.which("ffmpeg"):
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            dependencies["ffmpeg"] = result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
    
    # Check FFprobe
    if shutil.which("ffprobe"):
        try:
            result = subprocess.run(["ffprobe", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            dependencies["ffprobe"] = result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
    
    return dependencies