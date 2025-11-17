# UGC Video Variation Generator

Create AI-generated variations of User-Generated Content (UGC) videos. Transform one product review video into multiple unique versions with different AI avatars, voices, and scripts.

## What This Does

Take a single UGC video (like a protein powder review) and automatically create multiple variations:

- **Different Scripts**: AI rewrites the review with various personas and styles
- **Different Voices**: Generate voiceovers with multiple AI voices
- **Different Avatars**: Create videos with AI-generated presenters
- **Same Core Message**: Maintain the key points while varying the delivery

## Perfect For

- Product marketers creating multiple ad variations
- Content creators scaling UGC content
- A/B testing different presentation styles
- Creating diverse spokesperson variations
- Generating faceless YouTube content

## Features

### 🎬 Video Processing
- Download videos from YouTube and other platforms
- Extract and transcribe audio using Whisper AI
- Process local video files

### 📝 Script Generation
- AI-powered script variations using GPT-4
- Multiple persona styles (enthusiastic, professional, skeptical, etc.)
- Maintain core message while varying delivery
- Custom persona instructions

### 🎙️ Voice Generation
- Generate natural-sounding voiceovers with ElevenLabs
- Multiple voice options (male, female, different accents)
- Consistent quality across variations

### 👤 Avatar Videos
- Create talking head videos with HeyGen
- Alternative: D-ID integration
- Multiple avatar options
- Custom backgrounds

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd youtube
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### 4. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
HEYGEN_API_KEY=...
DID_API_KEY=...
```

### Getting API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **ElevenLabs**: https://elevenlabs.io/
- **HeyGen**: https://www.heygen.com/
- **D-ID**: https://www.d-id.com/

## Quick Start

### Process a YouTube Video

```bash
python ugc_video_generator.py --url "https://youtube.com/watch?v=VIDEO_ID" --variations 3
```

### Process a Local Video

```bash
python ugc_video_generator.py --video /path/to/video.mp4 --variations 5
```

### Process a Script File

```bash
python ugc_video_generator.py --script examples/example_script.txt --variations 3
```

## How It Works

### Complete Workflow

```
Original Video
    ↓
[1] Download & Extract Audio
    ↓
[2] Transcribe with Whisper AI
    ↓
[3] Generate Script Variations with GPT-4
    ↓
[4] Create Voice Variations with ElevenLabs
    ↓
[5] Generate Avatar Videos with HeyGen/D-ID
    ↓
Multiple Video Variations Ready!
```

### Step-by-Step Process

1. **Video Download**: Downloads video using yt-dlp
2. **Transcription**: Extracts script using OpenAI Whisper
3. **Script Generation**: Creates variations with different personas using GPT-4
4. **Voice Generation**: Generates audio for each variation with ElevenLabs
5. **Avatar Creation**: Creates talking head videos with HeyGen or D-ID

## Usage Examples

### Example 1: Basic Usage

```python
from ugc_video_generator import UGCVideoGenerator

generator = UGCVideoGenerator()

# Process a YouTube video
result = generator.process_video_url(
    url="https://youtube.com/watch?v=VIDEO_ID",
    num_variations=3,
    avatar_service='heygen'
)

print(f"Created {len(result['variations'])} variations")
```

### Example 2: Custom Personas

```python
from modules import ScriptVariationGenerator

generator = ScriptVariationGenerator()

original_script = """
Your original product review script here...
"""

# Define custom personas
personas = [
    "tech-savvy millennial who loves gadgets",
    "fitness enthusiast with 10 years of experience",
    "budget-conscious consumer who values quality"
]

variations = generator.generate_variations(
    original_script,
    num_variations=3,
    persona_variations=personas
)
```

### Example 3: Voice Only Generation

```python
from modules import VoiceGenerator

voice_gen = VoiceGenerator()

script = "Your review script here..."

# Generate multiple voice variations
audio_files = voice_gen.generate_multiple_voices(
    text=script,
    voice_names=['male_1', 'female_1', 'male_energetic'],
    base_filename='product_review'
)
```

## Project Structure

```
youtube/
├── modules/
│   ├── __init__.py
│   ├── video_downloader.py      # Download videos
│   ├── script_extractor.py      # Transcribe with Whisper
│   ├── script_variation_generator.py  # Generate script variations
│   ├── voice_generator.py       # ElevenLabs voice generation
│   └── avatar_generator.py      # HeyGen/D-ID avatar videos
├── examples/
│   ├── example_script.txt       # Sample script
│   └── quick_start.py          # Example code
├── output/                      # Generated content (gitignored)
│   ├── downloads/              # Downloaded videos
│   ├── transcripts/            # Extracted scripts
│   ├── variations/             # Script variations
│   └── audio/                  # Generated audio
├── ugc_video_generator.py      # Main CLI script
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment file
└── README.md                  # This file
```

## Output Files

After processing a video, you'll get:

```
output/
├── downloads/
│   └── original_video.mp4
├── transcripts/
│   ├── original_video_transcript.json
│   └── original_video_transcript.txt
├── variations/
│   ├── original_video_variations.json
│   ├── original_video_variation_1.txt
│   ├── original_video_variation_2.txt
│   └── original_video_variation_3.txt
└── audio/
    ├── original_video_variation_1.mp3
    ├── original_video_variation_2.mp3
    └── original_video_variation_3.mp3
```

## Advanced Configuration

### Whisper Model Sizes

Choose transcription accuracy vs. speed:

```python
# Faster, less accurate
extractor = ScriptExtractor(model_size='tiny')

# Balanced (default)
extractor = ScriptExtractor(model_size='base')

# More accurate, slower
extractor = ScriptExtractor(model_size='large')
```

### Custom Voice Settings

```python
voice_gen = VoiceGenerator()

# List available voices
voices = voice_gen.list_available_voices()

# Generate with specific voice
audio = voice_gen.generate_audio(
    text=script,
    voice_id="your_voice_id_here"
)
```

### Avatar Customization

```python
# HeyGen
avatar_gen = AvatarGenerator(service='heygen')
result = avatar_gen.heygen_create_video(
    script=script,
    avatar_id="custom_avatar_id",
    voice_id="custom_voice_id",
    background="#00FF00"  # Green background
)

# D-ID
avatar_gen = AvatarGenerator(service='did')
result = avatar_gen.did_create_video(
    script=script,
    presenter_id="custom_presenter_id"
)
```

## Cost Considerations

### API Pricing (Approximate)

- **OpenAI GPT-4**: ~$0.03 per 1K tokens (script generation)
- **ElevenLabs**: ~$0.30 per 1K characters (voice generation)
- **HeyGen**: ~$0.10-0.50 per video (varies by plan)
- **D-ID**: ~$0.10-0.30 per video (varies by plan)
- **Whisper**: Free (runs locally)

### Example Cost Per Video Set

For 3 variations of a 2-minute review:
- Script variations: ~$0.10
- Voice generation: ~$0.90
- Avatar videos: ~$0.90
- **Total: ~$1.90 for 3 complete video variations**

## Troubleshooting

### FFmpeg Not Found

```bash
# Install FFmpeg first
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # macOS
```

### API Key Errors

Make sure your `.env` file exists and has valid keys:
```bash
cat .env  # Check your keys
```

### Whisper Model Download Issues

The first time you run script extraction, Whisper will download models (~500MB). This is normal.

### Video Download Fails

Try updating yt-dlp:
```bash
pip install --upgrade yt-dlp
```

## Ethical Considerations

- ✅ Use with proper licenses and permissions
- ✅ Disclose AI-generated content where required
- ✅ Respect original creators' rights
- ✅ Follow platform terms of service
- ❌ Don't create misleading content
- ❌ Don't violate copyright laws
- ❌ Don't impersonate real people without consent

## Legal Notice

This tool is for educational and authorized commercial use only. Users are responsible for:

- Obtaining necessary rights and licenses
- Complying with copyright laws
- Following platform terms of service
- Disclosing AI-generated content
- Respecting intellectual property rights

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## Roadmap

- [ ] Support for more avatar services (Synthesia, Hour One)
- [ ] Batch processing of multiple videos
- [ ] Video editing and background replacement
- [ ] Web UI interface
- [ ] Template library for common products
- [ ] Analytics and A/B testing integration

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [OpenAI Whisper](https://github.com/openai/whisper) - Transcription
- [OpenAI GPT-4](https://openai.com/) - Script generation
- [ElevenLabs](https://elevenlabs.io/) - Voice synthesis
- [HeyGen](https://www.heygen.com/) - Avatar videos
- [D-ID](https://www.d-id.com/) - Avatar videos

---

**Made with ❤️ for content creators and marketers**
