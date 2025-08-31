"""
Video generation combining static images with mastered audio for social media platforms.
"""

import os
import subprocess
from pathlib import Path
from typing import Union, Optional, Tuple
from loguru import logger
from pydantic import BaseModel
from PIL import Image

from automatic_beer_goggles.config.platforms import PlatformConfig, AspectRatio, Resolution


class VideoGenerationConfig(BaseModel):
    """Configuration for video generation process."""
    output_format: str = "mp4"
    video_bitrate: Optional[str] = None  # e.g., "2M" for 2 Mbps
    audio_bitrate: str = "128k"
    fps: int = 30
    use_gpu_acceleration: bool = True
    temp_dir: Optional[str] = None


class VideoGenerator:
    """Handles video generation using FFmpeg."""
    
    def __init__(self, config: VideoGenerationConfig):
        self.config = config
        self.temp_dir = Path(config.temp_dir or "/tmp/beer_goggles")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def _prepare_image_for_platform(self, image_path: Path, platform_config: PlatformConfig, 
                                   aspect_ratio: AspectRatio) -> Path:
        """
        Prepare and resize image to match platform requirements.
        
        Args:
            image_path: Path to source PNG image
            platform_config: Platform configuration
            aspect_ratio: Target aspect ratio
            
        Returns:
            Path to prepared image file
        """
        target_resolution = platform_config.recommended_resolutions[aspect_ratio]
        
        # Create temporary processed image
        temp_image_path = self.temp_dir / f"processed_{image_path.stem}_{target_resolution}.png"
        
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    # Create a white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    img = background
                
                # Resize to target resolution with proper aspect ratio handling
                current_ratio = img.width / img.height
                target_ratio = target_resolution.width / target_resolution.height
                
                if abs(current_ratio - target_ratio) > 0.01:  # Ratios don't match
                    # Crop to fit target aspect ratio
                    if current_ratio > target_ratio:
                        # Image is wider, crop width
                        new_width = int(img.height * target_ratio)
                        left = (img.width - new_width) // 2
                        img = img.crop((left, 0, left + new_width, img.height))
                    else:
                        # Image is taller, crop height
                        new_height = int(img.width / target_ratio)
                        top = (img.height - new_height) // 2
                        img = img.crop((0, top, img.width, top + new_height))
                
                # Resize to exact target resolution
                img = img.resize((target_resolution.width, target_resolution.height), Image.Resampling.LANCZOS)
                
                # Save processed image
                img.save(temp_image_path, "PNG", quality=95)
                logger.info(f"Prepared image for {platform_config.name}: {target_resolution}")
                
                return temp_image_path
                
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            raise
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds using FFprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                logger.error(f"Failed to get audio duration: {result.stderr}")
                return 0.0
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    def _calculate_video_bitrate(self, duration: float, max_file_size_mb: int) -> str:
        """Calculate appropriate video bitrate to stay within file size limits."""
        if self.config.video_bitrate:
            return self.config.video_bitrate
        
        # Reserve 20% for audio and overhead
        available_size_mb = max_file_size_mb * 0.8
        available_bits = available_size_mb * 8 * 1024 * 1024  # Convert to bits
        
        # Calculate bitrate in bps, then convert to reasonable units
        bitrate_bps = available_bits / duration
        bitrate_kbps = bitrate_bps / 1000
        
        # Clamp to reasonable values (minimum 500k, maximum 10M)
        bitrate_kbps = max(500, min(10000, bitrate_kbps))
        
        return f"{int(bitrate_kbps)}k"
    
    def create_video(self, image_path: Union[str, Path], audio_path: Union[str, Path],
                    output_path: Union[str, Path], platform_config: PlatformConfig,
                    aspect_ratio: AspectRatio = None) -> bool:
        """
        Create a video combining static image with audio for a specific platform.
        
        Args:
            image_path: Path to PNG image
            audio_path: Path to mastered audio file
            output_path: Path for output video
            platform_config: Platform configuration
            aspect_ratio: Target aspect ratio (defaults to first supported ratio)
            
        Returns:
            True if successful, False otherwise
        """
        image_path = Path(image_path)
        audio_path = Path(audio_path)
        output_path = Path(output_path)
        
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return False
        
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return False
        
        # Use first supported aspect ratio if not specified
        if aspect_ratio is None:
            aspect_ratio = platform_config.aspect_ratios[0]
        
        if aspect_ratio not in platform_config.aspect_ratios:
            logger.error(f"Aspect ratio {aspect_ratio} not supported by {platform_config.name}")
            return False
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get audio duration and validate against platform limits
            audio_duration = self._get_audio_duration(audio_path)
            if audio_duration > platform_config.max_duration_seconds:
                logger.warning(f"Audio duration ({audio_duration}s) exceeds platform limit "
                             f"({platform_config.max_duration_seconds}s) for {platform_config.name}")
                # Truncate audio to platform limit
                audio_duration = platform_config.max_duration_seconds
            
            # Prepare image for platform
            processed_image = self._prepare_image_for_platform(image_path, platform_config, aspect_ratio)
            
            # Calculate appropriate bitrate
            video_bitrate = self._calculate_video_bitrate(audio_duration, platform_config.max_file_size_mb)
            
            logger.info(f"Creating {platform_config.name} video: {aspect_ratio}, "
                       f"duration: {audio_duration:.1f}s, bitrate: {video_bitrate}")
            
            # Build FFmpeg command
            cmd = ["ffmpeg", "-y"]  # Overwrite output files
            
            # GPU acceleration if available and enabled
            if self.config.use_gpu_acceleration:
                cmd.extend(["-hwaccel", "auto"])
            
            # Input image (loop for video duration)
            cmd.extend([
                "-loop", "1",
                "-i", str(processed_image),
                "-i", str(audio_path),
            ])
            
            # Video encoding settings
            resolution = platform_config.recommended_resolutions[aspect_ratio]
            cmd.extend([
                "-c:v", platform_config.video_codec.value,
                "-b:v", video_bitrate,
                "-s", str(resolution),
                "-r", str(self.config.fps),
                "-pix_fmt", "yuv420p",  # Ensure compatibility
            ])
            
            # Audio encoding settings
            cmd.extend([
                "-c:a", platform_config.audio_codec.value,
                "-b:a", self.config.audio_bitrate,
                "-ar", "44100",  # Standard sample rate for social media
            ])
            
            # Duration and timing
            cmd.extend([
                "-t", str(audio_duration),
                "-shortest",  # End when shortest stream ends
            ])
            
            # Output file
            cmd.append(str(output_path))
            
            # Execute FFmpeg command
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify output file size
                output_size_mb = output_path.stat().st_size / (1024 * 1024)
                if output_size_mb > platform_config.max_file_size_mb:
                    logger.warning(f"Output file ({output_size_mb:.1f} MB) exceeds platform limit "
                                 f"({platform_config.max_file_size_mb} MB)")
                
                logger.success(f"Video created successfully: {output_path.name} "
                             f"({output_size_mb:.1f} MB)")
                return True
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return False
        finally:
            # Cleanup temporary files
            if 'processed_image' in locals() and processed_image.exists():
                processed_image.unlink()
    
    def create_multi_platform_videos(self, image_path: Union[str, Path], audio_path: Union[str, Path],
                                    output_dir: Union[str, Path], platforms: list,
                                    base_filename: str = None) -> dict:
        """
        Create videos for multiple platforms from the same source materials.
        
        Args:
            image_path: Path to PNG image
            audio_path: Path to mastered audio file
            output_dir: Directory for output videos
            platforms: List of platform configurations
            base_filename: Base name for output files (derived from audio if not provided)
            
        Returns:
            Dictionary mapping platform names to output file paths (or None if failed)
        """
        image_path = Path(image_path)
        audio_path = Path(audio_path)
        output_dir = Path(output_dir)
        
        if base_filename is None:
            base_filename = audio_path.stem
        
        results = {}
        
        for platform_config in platforms:
            platform_name = platform_config.name.lower().replace(" ", "_")
            
            # Create platform-specific subdirectory
            platform_output_dir = output_dir / platform_name
            platform_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate videos for each supported aspect ratio
            for aspect_ratio in platform_config.aspect_ratios:
                ratio_suffix = aspect_ratio.value.replace(":", "x")
                output_filename = f"{base_filename}_{platform_name}_{ratio_suffix}.{self.config.output_format}"
                output_path = platform_output_dir / output_filename
                
                success = self.create_video(
                    image_path=image_path,
                    audio_path=audio_path,
                    output_path=output_path,
                    platform_config=platform_config,
                    aspect_ratio=aspect_ratio
                )
                
                key = f"{platform_config.name}_{aspect_ratio.value}"
                results[key] = output_path if success else None
        
        return results


def create_video_generator(config: Optional[VideoGenerationConfig] = None) -> VideoGenerator:
    """Create a VideoGenerator instance with default or provided configuration."""
    if config is None:
        config = VideoGenerationConfig()
    return VideoGenerator(config)