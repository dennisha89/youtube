# ComfyUI-UGC-Video-Generator

**Custom ComfyUI nodes** for creating AI-generated variations of User-Generated Content (UGC) videos. Transform one product review video into multiple unique versions with different AI avatars, voices, and scripts - all within ComfyUI!

## What This Does

Take a single UGC video (like a protein powder review) and automatically create multiple variations using ComfyUI nodes:

- **Different Scripts**: AI rewrites the review with various personas and styles
- **Different Voices**: Generate voiceovers with multiple AI voices (ElevenLabs)
- **Different Avatars**: Create videos with AI-generated presenters (HeyGen/D-ID)
- **Same Core Message**: Maintain the key points while varying the delivery
- **Visual Workflow**: Build your pipeline with drag-and-drop nodes in ComfyUI

## Perfect For

- Product marketers creating multiple ad variations
- Content creators scaling UGC content
- A/B testing different presentation styles
- Creating diverse spokesperson variations
- Generating faceless YouTube content
- ComfyUI users who want video generation capabilities

## ComfyUI Nodes

This extension adds 9 custom nodes to ComfyUI:

### Core Nodes

1. **UGC Video Downloader** 📥
   - Download videos from YouTube and other platforms
   - Returns video path and metadata

2. **UGC Script Extractor** 📝
   - Transcribe videos using Whisper AI
   - Choose model size (tiny/base/small/medium/large)
   - Returns script text and JSON

3. **UGC Script Variation Generator** ✨
   - Generate multiple script variations with GPT-4
   - Custom personas (enthusiastic, professional, skeptical, etc.)
   - Returns variations as JSON

4. **UGC Variation Selector** 🎯
   - Select specific variation from the list
   - Extract individual scripts for further processing

5. **UGC Voice Generator** 🎙️
   - Generate voices with ElevenLabs
   - 6 preset voices (male/female variants)
   - Returns audio file path

6. **UGC Avatar Generator** 👤
   - Create AI avatar videos (HeyGen or D-ID)
   - Custom avatars and backgrounds
   - Returns video job ID

7. **UGC Avatar Status Checker** ⏱️
   - Check avatar video generation status
   - Get video URL when complete

8. **UGC Avatar Downloader** 💾
   - Download completed avatar videos
   - Save to custom location

9. **UGC Text Input** ⌨️
   - Simple text input node
   - For scripts and custom prompts

## Installation

### Method 1: ComfyUI Manager (Recommended - Coming Soon)

1. Open ComfyUI Manager
2. Search for "UGC Video Generator"
3. Click Install
4. Restart ComfyUI

### Method 2: Manual Installation

1. **Navigate to ComfyUI custom nodes directory:**

```bash
cd ComfyUI/custom_nodes/
```

2. **Clone this repository:**

```bash
git clone https://github.com/YOUR_USERNAME/ComfyUI-UGC-Video-Generator.git
cd ComfyUI-UGC-Video-Generator
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Install FFmpeg** (if not already installed):

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

5. **Configure API Keys:**

```bash
cp .env.example .env
nano .env  # Edit and add your API keys
```

6. **Restart ComfyUI**

### Required API Keys

Edit `.env` and add your keys:

```env
OPENAI_API_KEY=sk-...          # Required for script variations
ELEVENLABS_API_KEY=...         # Required for voice generation
HEYGEN_API_KEY=...             # Optional - for HeyGen avatars
DID_API_KEY=...                # Optional - for D-ID avatars
```

**Get API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **ElevenLabs**: https://elevenlabs.io/
- **HeyGen**: https://www.heygen.com/
- **D-ID**: https://www.d-id.com/

## Quick Start

### 1. Load Example Workflow

1. Open ComfyUI
2. Click **"Load"** button
3. Navigate to: `custom_nodes/ComfyUI-UGC-Video-Generator/workflows/`
4. Load `01_basic_script_extraction.json`

### 2. Configure the Workflow

1. **UGC Video Downloader** node:
   - Enter YouTube URL

2. **UGC Script Extractor** node:
   - Choose Whisper model size (base recommended)

3. **UGC Script Variation** node:
   - Set number of variations (default: 3)

### 3. Queue Prompt

Click **"Queue Prompt"** and watch the magic happen!

### Example Workflows Included

- `01_basic_script_extraction.json` - Download → Extract → Generate Variations
- `02_voice_generation.json` - Generate multiple voice versions
- `03_complete_ugc_workflow.json` - Full pipeline to final video

## How It Works in ComfyUI

### Visual Node Workflow

```
┌─────────────────┐
│ Video Downloader│
│  (YouTube URL)  │
└────────┬────────┘
         ↓
┌────────────────┐
│Script Extractor│
│  (Whisper AI)  │
└────────┬───────┘
         ↓
┌────────────────────┐
│ Variation Generator│
│     (GPT-4)        │
└────────┬───────────┘
         ↓
┌──────────────────┐
│Variation Selector│
└────────┬─────────┘
         ↓
     ┌───┴───┐
     ↓       ↓
┌─────────┐ ┌──────────────┐
│  Voice  │ │    Avatar    │
│Generator│ │  Generator   │
│(ElevenLabs)│(HeyGen/D-ID)│
└─────────┘ └──────────────┘
         ↓
  Final Videos!
```

### Workflow Benefits

✅ **Visual**: See your entire pipeline
✅ **Modular**: Mix and match nodes
✅ **Flexible**: Create custom workflows
✅ **Reusable**: Save and share workflows
✅ **Parallel**: Run multiple variations at once

## Usage Examples

### Example 1: Basic Script Extraction

**Workflow**: YouTube URL → Script Variations

1. Add **UGC Video Downloader** node
2. Add **UGC Script Extractor** node
3. Add **UGC Script Variation** node
4. Connect: Downloader → Extractor → Variation Generator
5. Queue prompt!

### Example 2: Multiple Voice Versions

**Workflow**: Script → Multiple Voices

1. Add **UGC Text Input** node (paste your script)
2. Add 3x **UGC Voice Generator** nodes
3. Set different voice types (male_1, female_1, male_energetic)
4. Connect text input to all voice generators
5. Queue prompt!

Result: 3 different voice versions of your script

### Example 3: Complete UGC Pipeline

**Workflow**: URL → Final Videos

Load `03_complete_ugc_workflow.json` and follow the nodes:

1. Download video
2. Extract script
3. Generate 3 variations
4. Select variation #1
5. Generate voice
6. Create avatar video
7. Check status
8. Download final video

### Example 4: Custom Personas

In the **UGC Script Variation** node, use the "custom_personas" field:

```
tech-savvy millennial who loves gadgets
fitness enthusiast with 10 years experience
budget-conscious consumer who values quality
```

Each line becomes a different persona!

## Project Structure

```
ComfyUI-UGC-Video-Generator/
├── __init__.py                 # ComfyUI extension entry point
├── nodes.py                    # Custom node definitions
├── modules/                    # Core functionality
│   ├── __init__.py
│   ├── video_downloader.py     # Download videos
│   ├── script_extractor.py     # Transcribe with Whisper
│   ├── script_variation_generator.py  # Generate variations
│   ├── voice_generator.py      # ElevenLabs integration
│   └── avatar_generator.py     # HeyGen/D-ID integration
├── workflows/                  # Example ComfyUI workflows
│   ├── 01_basic_script_extraction.json
│   ├── 02_voice_generation.json
│   ├── 03_complete_ugc_workflow.json
│   └── README.md
├── examples/
│   └── example_script.txt      # Sample script
├── output/                     # Generated content (gitignored)
│   ├── downloads/              # Downloaded videos
│   ├── transcripts/            # Extracted scripts
│   ├── variations/             # Script variations
│   └── audio/                  # Generated audio
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment file
└── README.md                  # This file
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

### Nodes Don't Appear in ComfyUI

1. Make sure installation is in `ComfyUI/custom_nodes/`
2. Restart ComfyUI completely
3. Check console for error messages
4. Verify dependencies: `pip install -r requirements.txt`

### API Key Errors

1. Check `.env` file exists in the extension directory
2. Verify API keys are correct (no extra spaces)
3. Restart ComfyUI after adding keys

```bash
cd ComfyUI/custom_nodes/ComfyUI-UGC-Video-Generator/
cat .env  # Check your keys
```

### "Module not found" Errors

```bash
cd ComfyUI/custom_nodes/ComfyUI-UGC-Video-Generator/
pip install -r requirements.txt
```

### Whisper Model Download

First time using Script Extractor, Whisper downloads models (~500MB). This is normal and only happens once.

### Video Download Fails

```bash
pip install --upgrade yt-dlp
```

### Node Execution Fails

1. Check ComfyUI console for detailed errors
2. Verify all required inputs are connected
3. Check API rate limits and quotas
4. Try with smaller/simpler test cases first

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

- [x] Core ComfyUI nodes
- [x] Example workflows
- [ ] ComfyUI Manager integration
- [ ] Support for more avatar services (Synthesia, Hour One)
- [ ] Video editing nodes
- [ ] Background replacement nodes
- [ ] Batch processing workflows
- [ ] Template library workflows

## Credits

Built with:
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Node-based UI
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [OpenAI Whisper](https://github.com/openai/whisper) - Transcription
- [OpenAI GPT-4](https://openai.com/) - Script generation
- [ElevenLabs](https://elevenlabs.io/) - Voice synthesis
- [HeyGen](https://www.heygen.com/) - Avatar videos
- [D-ID](https://www.d-id.com/) - Avatar videos

---

**Made with ❤️ for ComfyUI users, content creators, and marketers**
