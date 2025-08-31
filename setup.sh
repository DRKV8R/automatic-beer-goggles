#!/bin/bash
# Quick setup script for Automatic Beer Goggles

set -e

echo "🍺 Automatic Beer Goggles - Quick Setup"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Installing..."
    
    # Detect OS and install FFmpeg
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Detected Linux. Installing FFmpeg via apt..."
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS. Installing FFmpeg via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
        brew install ffmpeg
    else
        echo "❌ Unsupported OS. Please install FFmpeg manually: https://ffmpeg.org/download.html"
        exit 1
    fi
else
    echo "✅ FFmpeg found: $(ffmpeg -version | head -n1)"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install the package in development mode
echo "🔧 Installing package in development mode..."
pip3 install -e .

# Create sample directories
echo "📁 Creating sample directories..."
mkdir -p examples/input/audio_files
mkdir -p examples/input
mkdir -p examples/output

# Create a sample image if PIL is available
echo "🖼️  Creating sample test image..."
python3 -c "
try:
    from PIL import Image
    import os
    
    # Create a sample brand image
    img = Image.new('RGB', (1920, 1080), color=(70, 130, 180))
    
    # Add some basic text if possible
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font
        try:
            font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 72)
        except:
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 72)
            except:
                font = ImageFont.load_default()
        
        # Draw centered text
        text = 'Sample Brand'
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)
    except ImportError:
        pass  # Skip text if ImageDraw/ImageFont not available
    
    img.save('examples/input/brand_image.png')
    print('✅ Sample brand image created: examples/input/brand_image.png')
    
    # Create a smaller square image for testing
    square_img = Image.new('RGB', (1080, 1080), color=(255, 140, 0))
    square_img.save('examples/input/square_image.png')
    print('✅ Sample square image created: examples/input/square_image.png')
    
except ImportError:
    print('⚠️  PIL not available. Please create sample images manually.')
"

# Create a sample audio file using FFmpeg
echo "🎵 Creating sample audio file..."
ffmpeg -f lavfi -i "sine=frequency=440:duration=10" -ar 44100 -ac 2 examples/input/sample_audio.wav -y 2>/dev/null
echo "✅ Sample audio created: examples/input/sample_audio.wav"

# Test the installation
echo "🧪 Testing installation..."
if python3 -m automatic_beer_goggles.cli info >/dev/null 2>&1; then
    echo "✅ Installation successful!"
else
    echo "❌ Installation test failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 Setup complete! You can now use Automatic Beer Goggles."
echo ""
echo "Quick start commands:"
echo "  • Check system info:    python3 -m automatic_beer_goggles.cli info"
echo "  • Create single video:  python3 -m automatic_beer_goggles.cli create-video examples/input/brand_image.png examples/input/sample_audio.wav output.mp4 --platform youtube"
echo "  • Run example script:   python3 examples/basic_workflow.py"
echo ""
echo "See README.md for detailed usage instructions."