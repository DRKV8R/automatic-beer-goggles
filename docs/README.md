# Automatic Beer Goggles Documentation

Welcome to the official documentation site for Automatic Beer Goggles!

## Quick Links

- 🏠 [Home](https://drkv8r.github.io/automatic-beer-goggles)
- 📂 [GitHub Repository](https://github.com/DRKV8R/automatic-beer-goggles)
- 🚀 [Getting Started](#installation)
- 📚 [CLI Documentation](#cli-commands)

## Overview

Automatic Beer Goggles is a powerful Python toolkit for automated video creation, specifically designed for social media platforms. It combines static images with mastered audio to create professional-quality videos optimized for different social media platforms.

### Key Features

- **Professional Audio Mastering**: Integration with iZotope Ozone 11 and FFmpeg fallback
- **Multi-Platform Support**: YouTube, Instagram, TikTok, Facebook, Twitter, LinkedIn
- **Intelligent Optimization**: Automatic resolution, aspect ratio, and bitrate adjustment
- **Batch Processing**: Concurrent processing of multiple files
- **CLI Interface**: Rich command-line interface with progress tracking

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video/audio processing)
- iZotope Ozone 11 (optional, for advanced audio mastering)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/DRKV8R/automatic-beer-goggles.git
cd automatic-beer-goggles

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Run the quick setup script (optional)
./setup.sh
```

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## Quick Start Examples

### Check System Information
```bash
python -m automatic_beer_goggles.cli info
```

### Master Audio File
```bash
python -m automatic_beer_goggles.cli master-audio \
    input/audio.wav \
    output/mastered_audio.wav \
    --target-lufs -14.0
```

### Create Single Video
```bash
python -m automatic_beer_goggles.cli create-video \
    image.png \
    audio.wav \
    output.mp4 \
    --platform youtube \
    --aspect-ratio 16:9
```

### Batch Process Multiple Files
```bash
python -m automatic_beer_goggles.cli batch-process \
    audio_directory/ \
    brand_image.png \
    output_directory/ \
    --platforms youtube instagram tiktok \
    --max-jobs 4
```

## CLI Commands

### `info`
Display system information and check dependencies.

### `create-video`
Create a video from image and audio for a specific platform.

**Options:**
- `--platform`: Target social media platform (required)
- `--aspect-ratio`: Aspect ratio (e.g., 16:9, 1:1, 9:16)
- `--video-bitrate`: Video bitrate (e.g., 2M)
- `--audio-bitrate`: Audio bitrate (default: 128k)
- `--fps`: Frames per second (default: 30)

### `master-audio`
Master a single audio file using iZotope Ozone 11 or FFmpeg.

**Options:**
- `--preset`: iZotope Ozone preset name (default: "Master Assistant")
- `--target-lufs`: Target LUFS for normalization (default: -14.0)
- `--ozone-path`: Path to iZotope Ozone executable

### `batch-process`
Batch process multiple audio files into videos for multiple platforms.

**Options:**
- `--platforms`: Target platforms (can be specified multiple times)
- `--audio-pattern`: Audio file pattern (default: *.wav)
- `--max-jobs`: Maximum concurrent jobs (default: 4)
- `--resume`: Resume from previous run
- `--report-file`: Export job report to file

## Supported Platforms

| Platform  | Aspect Ratios   | Max Duration | Max File Size | Notes                                    |
|-----------|-----------------|--------------|---------------|------------------------------------------|
| Facebook  | 16:9, 9:16      | 240m 0s      | 4.0 GB        | Stories limited to 2 minutes           |
| Instagram | 1:1, 9:16       | 10m 0s       | 4.0 GB        | Square or vertical recommended          |
| YouTube   | 16:9, 9:16      | 15m 0s       | 128.0 GB      | 1080p minimum, Shorts 60s max          |
| TikTok    | 9:16            | 3m 0s        | 288.0 MB      | Forced vertical videos                  |
| Twitter   | 1:1, 16:9       | 2m 20s       | 512.0 MB      | Optimized square videos recommended     |
| LinkedIn  | 16:9, 1:1, 9:16 | 3m 0s        | 5.0 GB        | Professional content, high-quality audio|

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues, questions, or contributions, please visit the GitHub repository:
[https://github.com/DRKV8R/automatic-beer-goggles](https://github.com/DRKV8R/automatic-beer-goggles)
