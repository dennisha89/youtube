# Usage Guide - UGC Video Variation Generator

## Table of Contents

1. [First Time Setup](#first-time-setup)
2. [Basic Usage](#basic-usage)
3. [Common Scenarios](#common-scenarios)
4. [API Key Setup](#api-key-setup)
5. [Best Practices](#best-practices)

## First Time Setup

### 1. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Check system requirements
- Create virtual environment
- Install dependencies
- Create configuration files
- Set up output directories

### 2. Add API Keys

Edit the `.env` file:

```bash
nano .env
```

Add your API keys (get them from the respective websites):

```
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=...
HEYGEN_API_KEY=...
DID_API_KEY=...
```

Save and exit (Ctrl+X, then Y, then Enter).

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Basic Usage

### Scenario 1: I have a YouTube URL

```bash
python ugc_video_generator.py --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

This will:
1. Download the video
2. Extract the script
3. Generate 3 variations (default)
4. Create voice files
5. Generate avatar videos (if API keys are set)

### Scenario 2: I have a video file on my computer

```bash
python ugc_video_generator.py --video /path/to/my/video.mp4
```

### Scenario 3: I just have a script/text

```bash
python ugc_video_generator.py --script my_review.txt --variations 5
```

### Scenario 4: I want more variations

```bash
python ugc_video_generator.py --url "YOUTUBE_URL" --variations 10
```

### Scenario 5: I want to use D-ID instead of HeyGen

```bash
python ugc_video_generator.py --url "YOUTUBE_URL" --avatar-service did
```

## Common Scenarios

### Creating Product Review Variations

**Starting with YouTube video:**

1. Find a product review video on YouTube
2. Copy the URL
3. Run:
   ```bash
   python ugc_video_generator.py --url "YOUTUBE_URL" --variations 5
   ```
4. Check the `output/` directory for results

**Starting with your own script:**

1. Write your review in a text file (`my_review.txt`)
2. Run:
   ```bash
   python ugc_video_generator.py --script my_review.txt --variations 3
   ```
3. Get variations in `output/variations/`

### Creating Variations with Specific Personas

Edit `ugc_video_generator.py` or use Python directly:

```python
from modules import ScriptVariationGenerator

generator = ScriptVariationGenerator()

script = """
Your product review here...
"""

# Define your own personas
personas = [
    "young enthusiastic tiktoker who uses lots of slang",
    "serious scientist who focuses on data and studies",
    "mom of 3 who cares about family-friendly products"
]

variations = generator.generate_variations(
    script,
    num_variations=3,
    persona_variations=personas
)

generator.save_variations(variations, "custom_review")
```

### Voice-Only Generation (No Video)

If you just want different voice versions:

```python
from modules import VoiceGenerator

voice_gen = VoiceGenerator()

script = "Your review script..."

# Generate 3 different voices
voices = voice_gen.generate_multiple_voices(
    text=script,
    voice_names=['male_1', 'female_1', 'male_energetic'],
    base_filename='my_review'
)
```

Results will be in `output/audio/`.

### Batch Processing Multiple Videos

Create a script like this:

```python
from ugc_video_generator import UGCVideoGenerator

generator = UGCVideoGenerator()

urls = [
    "https://youtube.com/watch?v=VIDEO1",
    "https://youtube.com/watch?v=VIDEO2",
    "https://youtube.com/watch?v=VIDEO3",
]

for url in urls:
    try:
        result = generator.process_video_url(url, num_variations=3)
        print(f"✓ Processed: {url}")
    except Exception as e:
        print(f"✗ Failed: {url} - {e}")
```

## API Key Setup

### OpenAI (Required for script variations)

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. Add to `.env`: `OPENAI_API_KEY=sk-proj-...`

**Cost**: ~$0.03 per variation

### ElevenLabs (Required for voice generation)

1. Go to https://elevenlabs.io/
2. Sign up for an account
3. Go to your profile → API Keys
4. Copy your API key
5. Add to `.env`: `ELEVENLABS_API_KEY=...`

**Cost**: ~$0.30 per minute of audio

### HeyGen (Optional - for avatar videos)

1. Go to https://www.heygen.com/
2. Sign up for an account
3. Navigate to API section
4. Get your API key
5. Add to `.env`: `HEYGEN_API_KEY=...`

**Cost**: ~$0.10-0.50 per video

### D-ID (Alternative to HeyGen)

1. Go to https://www.d-id.com/
2. Create an account
3. Get API credentials
4. Add to `.env`: `DID_API_KEY=...`

**Cost**: ~$0.10-0.30 per video

## Best Practices

### 1. Start Small

Begin with 2-3 variations to test before scaling up:

```bash
python ugc_video_generator.py --url "URL" --variations 2
```

### 2. Check Output Regularly

Review the generated content in `output/` directory:
- `transcripts/` - Check if transcription is accurate
- `variations/` - Review script variations
- `audio/` - Listen to voice quality

### 3. Manage Costs

- Use smaller Whisper models for faster processing (`base` instead of `large`)
- Generate scripts and review before generating voices/videos
- Use free tier APIs when possible

### 4. Quality Control

Always review generated variations:

1. **Script Quality**: Read the variations to ensure they make sense
2. **Voice Quality**: Listen to audio files before using in videos
3. **Avatar Quality**: Check first avatar video before batch processing

### 5. Optimize Workflow

**Step 1: Extract and Review**
```bash
# Just download and transcribe first
python ugc_video_generator.py --url "URL"
# Review the transcript in output/transcripts/
```

**Step 2: Generate Variations**
```bash
# Generate scripts only
# Review variations in output/variations/
```

**Step 3: Generate Media**
```bash
# Only generate voices/avatars for approved variations
```

### 6. File Organization

Keep your projects organized:

```
my-product-campaign/
├── original-videos/
├── scripts/
│   ├── variation-1.txt
│   ├── variation-2.txt
│   └── variation-3.txt
├── audio/
├── final-videos/
└── notes.txt
```

## Troubleshooting Quick Fixes

### "Module not found" error
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "API key not set" warning
```bash
nano .env
# Add the missing API key
```

### Video download fails
```bash
pip install --upgrade yt-dlp
```

### Slow transcription
Use a smaller Whisper model:
```python
extractor = ScriptExtractor(model_size='base')  # instead of 'large'
```

### Out of API credits
Check your usage at:
- OpenAI: https://platform.openai.com/usage
- ElevenLabs: Your account dashboard
- HeyGen: Your account dashboard

## Getting Help

1. Check the main [README.md](README.md)
2. Review [examples/quick_start.py](examples/quick_start.py)
3. Run the test script:
   ```bash
   python examples/quick_start.py
   ```

## Next Steps

Once you're comfortable with basic usage:

1. Experiment with custom personas
2. Try different voice combinations
3. Test both HeyGen and D-ID for avatars
4. Create your own automation scripts
5. Integrate with your content workflow

Happy creating!
