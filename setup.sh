#!/bin/bash
# Setup script for UGC Video Variation Generator

echo "=========================================="
echo "UGC Video Variation Generator - Setup"
echo "=========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check FFmpeg
echo ""
echo "Checking FFmpeg..."
ffmpeg -version > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  FFmpeg not found."
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
else
    echo "✅ FFmpeg found"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
    echo "   nano .env"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create output directories
echo ""
echo "Creating output directories..."
mkdir -p output/downloads
mkdir -p output/transcripts
mkdir -p output/variations
mkdir -p output/audio
mkdir -p temp
echo "✅ Directories created"

# Test import
echo ""
echo "Testing module imports..."
python3 -c "import modules; print('✅ Modules imported successfully')"

if [ $? -ne 0 ]; then
    echo "❌ Module import failed"
    exit 1
fi

# Make main script executable
chmod +x ugc_video_generator.py
chmod +x examples/quick_start.py

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the example:"
echo "   python examples/quick_start.py"
echo ""
echo "4. Or process a video:"
echo "   python ugc_video_generator.py --url 'YOUTUBE_URL'"
echo ""
echo "=========================================="
