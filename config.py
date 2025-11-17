import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
HEYGEN_API_KEY = os.getenv('HEYGEN_API_KEY')
DID_API_KEY = os.getenv('DID_API_KEY')

# Directories
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
TEMP_DIR = os.getenv('TEMP_DIR', './temp')
DOWNLOADS_DIR = os.path.join(OUTPUT_DIR, 'downloads')
TRANSCRIPTS_DIR = os.path.join(OUTPUT_DIR, 'transcripts')
VARIATIONS_DIR = os.path.join(OUTPUT_DIR, 'variations')
AUDIO_DIR = os.path.join(OUTPUT_DIR, 'audio')

# Settings
VARIATIONS_PER_VIDEO = int(os.getenv('VARIATIONS_PER_VIDEO', 3))

# Create directories
for directory in [OUTPUT_DIR, TEMP_DIR, DOWNLOADS_DIR, TRANSCRIPTS_DIR, VARIATIONS_DIR, AUDIO_DIR]:
    os.makedirs(directory, exist_ok=True)
