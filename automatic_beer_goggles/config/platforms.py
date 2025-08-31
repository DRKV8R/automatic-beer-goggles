"""
Platform-specific configuration for social media video formats.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class AspectRatio(str, Enum):
    """Standard aspect ratios for social media platforms."""
    SQUARE = "1:1"
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    TWITTER_LANDSCAPE = "16:9"


class VideoCodec(str, Enum):
    """Supported video codecs."""
    H264 = "h264"
    H265 = "h265"


class AudioCodec(str, Enum):
    """Supported audio codecs."""
    AAC = "aac"
    AAC_LC = "aac_lc"


class Resolution(BaseModel):
    """Video resolution configuration."""
    width: int
    height: int
    
    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


class PlatformConfig(BaseModel):
    """Configuration for a specific social media platform."""
    name: str
    supported_formats: List[str]
    aspect_ratios: List[AspectRatio]
    max_duration_seconds: int
    max_file_size_mb: int
    video_codec: VideoCodec
    audio_codec: AudioCodec
    recommended_resolutions: Dict[AspectRatio, Resolution]
    max_bitrate_kbps: Optional[int] = None
    audio_bitrate_kbps: int = 128
    notes: Optional[str] = None


# Platform-specific configurations
PLATFORM_CONFIGS = {
    "facebook": PlatformConfig(
        name="Facebook",
        supported_formats=["mp4", "mov"],
        aspect_ratios=[AspectRatio.LANDSCAPE, AspectRatio.PORTRAIT],
        max_duration_seconds=14400,  # 240 minutes for posts
        max_file_size_mb=4096,  # 4 GB
        video_codec=VideoCodec.H264,
        audio_codec=AudioCodec.AAC_LC,
        recommended_resolutions={
            AspectRatio.LANDSCAPE: Resolution(width=1920, height=1080),
            AspectRatio.PORTRAIT: Resolution(width=1080, height=1920),
        },
        notes="Stories limited to 2 minutes"
    ),
    
    "instagram": PlatformConfig(
        name="Instagram",
        supported_formats=["mp4"],
        aspect_ratios=[AspectRatio.SQUARE, AspectRatio.PORTRAIT],
        max_duration_seconds=600,  # 10 minutes for posts
        max_file_size_mb=4096,
        video_codec=VideoCodec.H264,
        audio_codec=AudioCodec.AAC,
        recommended_resolutions={
            AspectRatio.SQUARE: Resolution(width=1080, height=1080),
            AspectRatio.PORTRAIT: Resolution(width=1080, height=1920),
        },
        notes="Stories/Reels 15-90 seconds recommended"
    ),
    
    "youtube": PlatformConfig(
        name="YouTube",
        supported_formats=["mp4", "mov", "avi", "webm"],
        aspect_ratios=[AspectRatio.LANDSCAPE, AspectRatio.PORTRAIT],
        max_duration_seconds=900,  # 15 minutes standard
        max_file_size_mb=131072,  # 128 GB
        video_codec=VideoCodec.H264,
        audio_codec=AudioCodec.AAC,
        recommended_resolutions={
            AspectRatio.LANDSCAPE: Resolution(width=1920, height=1080),
            AspectRatio.PORTRAIT: Resolution(width=1080, height=1920),
        },
        notes="Shorts limited to 60 seconds, render at 1080p minimum"
    ),
    
    "tiktok": PlatformConfig(
        name="TikTok",
        supported_formats=["mp4", "mov"],
        aspect_ratios=[AspectRatio.PORTRAIT],
        max_duration_seconds=180,  # 3 minutes
        max_file_size_mb=288,  # 287.6 MB typical max
        video_codec=VideoCodec.H264,
        audio_codec=AudioCodec.AAC_LC,
        recommended_resolutions={
            AspectRatio.PORTRAIT: Resolution(width=1080, height=1920),
        },
        notes="Forced vertical videos, keep file size small"
    ),
    
    "twitter": PlatformConfig(
        name="Twitter",
        supported_formats=["mp4", "mov"],
        aspect_ratios=[AspectRatio.SQUARE, AspectRatio.LANDSCAPE],
        max_duration_seconds=140,  # 2 minutes 20 seconds
        max_file_size_mb=512,
        video_codec=VideoCodec.H264,
        audio_codec=AudioCodec.AAC,
        recommended_resolutions={
            AspectRatio.SQUARE: Resolution(width=1080, height=1080),
            AspectRatio.LANDSCAPE: Resolution(width=1280, height=720),
        },
        notes="Optimized square videos, shorter lengths recommended"
    ),
    
    "linkedin": PlatformConfig(
        name="LinkedIn",
        supported_formats=["mp4"],
        aspect_ratios=[AspectRatio.LANDSCAPE, AspectRatio.SQUARE, AspectRatio.PORTRAIT],
        max_duration_seconds=180,  # 3 minutes typical max
        max_file_size_mb=5120,  # 5 GB
        video_codec=VideoCodec.H264,
        audio_codec=AudioCodec.AAC,
        recommended_resolutions={
            AspectRatio.LANDSCAPE: Resolution(width=1920, height=1080),
            AspectRatio.SQUARE: Resolution(width=1080, height=1080),
            AspectRatio.PORTRAIT: Resolution(width=1080, height=1920),
        },
        notes="16:9 default, supports all ratios, high-quality audio"
    ),
}


def get_platform_config(platform: str) -> PlatformConfig:
    """Get configuration for a specific platform."""
    if platform.lower() not in PLATFORM_CONFIGS:
        raise ValueError(f"Unsupported platform: {platform}")
    return PLATFORM_CONFIGS[platform.lower()]


def list_supported_platforms() -> List[str]:
    """Get list of all supported platforms."""
    return list(PLATFORM_CONFIGS.keys())