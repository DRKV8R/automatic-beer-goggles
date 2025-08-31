#!/usr/bin/env python3
"""
Example script: Basic workflow for creating social media videos
"""

import sys
from pathlib import Path

# Add the project root to Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from automatic_beer_goggles.audio.mastering import AudioMasteringConfig, create_audio_masterer
from automatic_beer_goggles.video.generation import VideoGenerationConfig, create_video_generator
from automatic_beer_goggles.config.platforms import get_platform_config, list_supported_platforms
from loguru import logger


def main():
    """Example of basic workflow for creating videos."""
    
    # Setup logging
    logger.add(sys.stderr, level="INFO")
    
    # Configuration
    input_audio = Path("input/audio.wav")
    input_image = Path("input/image.png")
    output_dir = Path("output")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Check if input files exist
    if not input_audio.exists():
        logger.error(f"Input audio file not found: {input_audio}")
        return 1
    
    if not input_image.exists():
        logger.error(f"Input image file not found: {input_image}")
        return 1
    
    # Step 1: Master the audio
    logger.info("Step 1: Mastering audio...")
    audio_config = AudioMasteringConfig(
        target_lufs=-14.0,  # Streaming standard
        normalize_loudness=True
    )
    
    masterer = create_audio_masterer(audio_config)
    mastered_audio = output_dir / "mastered_audio.wav"
    
    if not masterer.master_audio_file(input_audio, mastered_audio):
        logger.error("Audio mastering failed")
        return 1
    
    logger.success(f"Audio mastered: {mastered_audio}")
    
    # Step 2: Create videos for multiple platforms
    logger.info("Step 2: Creating platform-specific videos...")
    
    video_config = VideoGenerationConfig(
        fps=30,
        audio_bitrate="128k"
    )
    
    generator = create_video_generator(video_config)
    
    # Target platforms
    target_platforms = ["youtube", "instagram", "tiktok"]
    
    for platform_name in target_platforms:
        logger.info(f"Creating videos for {platform_name}...")
        
        platform_config = get_platform_config(platform_name)
        
        # Create videos for each supported aspect ratio
        platform_results = generator.create_multi_platform_videos(
            image_path=input_image,
            audio_path=mastered_audio,
            output_dir=output_dir / "videos",
            platforms=[platform_config],
            base_filename=f"video_{platform_name}"
        )
        
        # Report results
        for video_key, video_path in platform_results.items():
            if video_path:
                logger.success(f"Created: {video_path}")
            else:
                logger.error(f"Failed to create: {video_key}")
    
    logger.info("Workflow completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())