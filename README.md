# Automatic Beer Goggles

🍺 **Automated mastered audio-image video creation for social media platforms**

An advanced Python system that automates the creation of videos combining static PNG images with mastered audio files, producing platform-optimized videos for broad social video and audio distribution.

## Features

- **Multi-Platform Support**: Create videos optimized for Facebook, Instagram, YouTube, TikTok, Twitter, and LinkedIn
- **Audio Mastering**: Integrates with iZotope Ozone 11 or uses FFmpeg fallback for audio mastering
- **Platform-Specific Optimization**: Automatically adjusts resolution, aspect ratio, bitrate, and codecs for each platform
- **Batch Processing**: Process multiple audio files simultaneously with configurable concurrency
- **Intelligent Scaling**: Automatically manages file sizes and durations according to platform limits
- **CLI Interface**: User-friendly command-line interface with rich formatting and progress tracking

## Supported Platforms

| Platform  | Aspect Ratios   | Max Duration | Max File Size | Notes                                    |
|-----------|-----------------|--------------|---------------|------------------------------------------|
| Facebook  | 16:9, 9:16      | 240m 0s      | 4.0 GB        | Stories limited to 2 minutes           |
| Instagram | 1:1, 9:16       | 10m 0s       | 4.0 GB        | Square or vertical recommended          |
| YouTube   | 16:9, 9:16      | 15m 0s       | 128.0 GB      | 1080p minimum, Shorts 60s max          |
| TikTok    | 9:16            | 3m 0s        | 288.0 MB      | Forced vertical videos                  |
| Twitter   | 1:1, 16:9       | 2m 20s       | 512.0 MB      | Optimized square videos recommended     |
| LinkedIn  | 16:9, 1:1, 9:16 | 3m 0s        | 5.0 GB        | Professional content, high-quality audio|

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required for video/audio processing)
- iZotope Ozone 11 (optional, for advanced audio mastering)

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

### Install the Package

```bash
# Clone the repository
git clone https://github.com/DRKV8R/automatic-beer-goggles.git
cd automatic-beer-goggles

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

### 1. Check System Information

```bash
python -m automatic_beer_goggles.cli info
```

This command displays:
- System information (CPU, memory, disk space)
- Dependency status (FFmpeg, FFprobe)
- Supported platforms and their specifications

### 2. Create a Single Video

```bash
python -m automatic_beer_goggles.cli create-video \
    path/to/image.png \
    path/to/audio.wav \
    output/video.mp4 \
    --platform youtube \
    --aspect-ratio 16:9
```

### 3. Master Audio File

```bash
python -m automatic_beer_goggles.cli master-audio \
    input/audio.wav \
    output/mastered_audio.wav \
    --target-lufs -14.0
```

### 4. Batch Process Multiple Files

```bash
python -m automatic_beer_goggles.cli batch-process \
    audio_directory/ \
    path/to/image.png \
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

### `batch-master`
Batch master multiple audio files.

**Options:**
- `--audio-pattern`: Audio file pattern (default: *.wav)
- `--preset`: iZotope Ozone preset name
- `--target-lufs`: Target LUFS for normalization
- `--ozone-path`: Path to iZotope Ozone executable

## Configuration

### Audio Mastering Configuration

The system uses intelligent audio mastering with the following defaults:

- **Target LUFS**: -14.0 (streaming standard)
- **Sample Rate**: 44.1 kHz
- **Bit Depth**: 16-bit (for compatibility)
- **Normalization**: Enabled with loudness standards

### Video Generation Configuration

Videos are automatically optimized based on platform requirements:

- **Codec**: H.264 in MP4 containers
- **Audio**: AAC encoding at 128 kbps
- **Bitrate**: Automatically calculated based on file size limits
- **Resolution**: Platform-specific optimal resolutions

## Project Structure

```
automatic-beer-goggles/
├── automatic_beer_goggles/
│   ├── audio/
│   │   └── mastering.py          # Audio mastering functionality
│   ├── config/
│   │   └── platforms.py          # Platform-specific configurations
│   ├── video/
│   │   └── generation.py         # Video generation and encoding
│   ├── orchestration/
│   │   └── workflow.py           # Batch processing orchestration
│   ├── utils/
│   │   └── file_utils.py         # File validation and utilities
│   └── cli.py                    # Command-line interface
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Technical Architecture

### Audio Mastering Workflow

1. **Detection**: Automatically detects iZotope Ozone 11 installation
2. **Mastering**: Applies Master Assistant presets or FFmpeg loudness normalization
3. **Export**: Maintains source naming with "_mastered" suffix
4. **Validation**: Ensures audio quality and format compliance

### Video Generation Pipeline

1. **Image Processing**: Resizes and crops images to match platform requirements
2. **Duration Calculation**: Matches video length to audio duration (respecting platform limits)
3. **Encoding**: Uses FFmpeg with optimized settings for each platform
4. **Validation**: Checks file size and format compliance

### Platform Optimization

Each platform has specific optimizations:

- **Aspect Ratio Handling**: Intelligent cropping and scaling
- **Bitrate Management**: Dynamic calculation based on file size limits
- **Codec Selection**: Platform-specific video and audio codecs
- **Resolution Targeting**: Optimal resolutions for each platform

## Examples

### Basic Workflow

```bash
# 1. Create test audio and image files
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" test_audio.wav
python3 -c "from PIL import Image; Image.new('RGB', (1920, 1080), 'blue').save('test_image.png')"

# 2. Master the audio
python -m automatic_beer_goggles.cli master-audio test_audio.wav mastered_audio.wav

# 3. Create videos for multiple platforms
python -m automatic_beer_goggles.cli create-video test_image.png mastered_audio.wav youtube_video.mp4 --platform youtube
python -m automatic_beer_goggles.cli create-video test_image.png mastered_audio.wav instagram_video.mp4 --platform instagram
```

### Advanced Batch Processing

```bash
# Process an entire directory of audio files
python -m automatic_beer_goggles.cli batch-process \
    ./audio_files/ \
    ./brand_image.png \
    ./output/ \
    --platforms youtube instagram tiktok twitter \
    --max-jobs 8 \
    --report-file processing_report.json
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Install FFmpeg and ensure it's in your PATH
2. **iZotope Ozone not detected**: Specify the path using `--ozone-path`
3. **Video generation fails**: Check available disk space and file permissions
4. **Large file sizes**: Reduce video bitrate or increase compression

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python -m automatic_beer_goggles.cli --verbose [command]
```

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
