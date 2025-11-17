# Complete Automation Guide - UGC Video Generator

This guide shows you how to fully automate UGC video creation from start to finish.

## Table of Contents

1. [System Overview](#system-overview)
2. [Step-by-Step Setup](#step-by-step-setup)
3. [Manual Workflow (ComfyUI)](#manual-workflow-comfyui)
4. [Full Automation](#full-automation)
5. [Automation Scripts](#automation-scripts)
6. [Scheduling & Batch Processing](#scheduling--batch-processing)

## System Overview

### What You Can Automate

1. **Input**: YouTube video URL or product name
2. **Process**: Automatically generate 3-10 variations
3. **Output**: Ready-to-upload video files

### The Automation Pipeline

```
Input (URL or Product)
    ↓
Download Video (automated)
    ↓
Extract Script (automated)
    ↓
Generate Variations (automated)
    ↓
Create Voices (automated)
    ↓
Generate Avatar Videos (automated)
    ↓
Download & Store (automated)
    ↓
Ready for Upload!
```

## Step-by-Step Setup

### Phase 1: Install ComfyUI (if not already installed)

1. **Install ComfyUI**

```bash
cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

2. **Test ComfyUI Works**

```bash
python main.py
# Open browser to http://127.0.0.1:8188
```

### Phase 2: Install UGC Video Generator Nodes

1. **Navigate to custom nodes**

```bash
cd ComfyUI/custom_nodes/
```

2. **Clone this repository**

```bash
git clone YOUR_REPO_URL ComfyUI-UGC-Video-Generator
cd ComfyUI-UGC-Video-Generator
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure API keys**

```bash
cp .env.example .env
nano .env
```

Add your keys:
```
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=...
HEYGEN_API_KEY=...
```

5. **Restart ComfyUI**

```bash
cd ../../
python main.py
```

### Phase 3: Test the Workflow

1. Open ComfyUI in browser
2. Load workflow: `custom_nodes/ComfyUI-UGC-Video-Generator/workflows/03_complete_ugc_workflow.json`
3. Edit Video Downloader node with a test YouTube URL
4. Click "Queue Prompt"
5. Watch it work!

## Manual Workflow (ComfyUI)

### Creating Videos in ComfyUI (Step by Step)

#### Step 1: Download Video

1. Add **UGC Video Downloader** node
2. Enter YouTube URL: `https://youtube.com/watch?v=VIDEO_ID`
3. Connect output to next node

#### Step 2: Extract Script

1. Add **UGC Script Extractor** node
2. Connect video_path from downloader
3. Choose model size: `base` (recommended)

#### Step 3: Generate Variations

1. Add **UGC Script Variation** node
2. Connect script_text from extractor
3. Set number of variations: `3`
4. (Optional) Add custom personas in the custom_personas field

#### Step 4: Process Each Variation

For each variation you want to create:

1. Add **UGC Variation Selector** node
   - Connect variations_json
   - Set index: 0, 1, 2, etc.

2. Add **UGC Voice Generator** node
   - Connect script from selector
   - Choose voice type
   - Set filename

3. Add **UGC Avatar Generator** node
   - Connect script from selector
   - Choose service (heygen or did)
   - Set background color

4. Add **UGC Avatar Status Checker** node
   - Connect video_id from generator
   - Use to monitor progress

5. Add **UGC Avatar Downloader** node
   - Connect video_id from generator
   - Set output filename
   - Downloads when ready

#### Step 5: Queue and Monitor

1. Click **"Queue Prompt"**
2. Watch ComfyUI console for progress
3. Videos will be saved to `output/variations/`

## Full Automation

### Option 1: ComfyUI API Automation

You can automate ComfyUI workflows using its API. Here's how:

#### 1. Create Automation Script

Create `automate_ugc.py`:

```python
#!/usr/bin/env python3
"""
Automated UGC Video Generator using ComfyUI API
"""

import json
import requests
import time

COMFYUI_URL = "http://127.0.0.1:8188"

def load_workflow(workflow_path):
    """Load a ComfyUI workflow JSON"""
    with open(workflow_path, 'r') as f:
        return json.load(f)

def update_workflow_url(workflow, video_url):
    """Update the video URL in the workflow"""
    # Find the Video Downloader node (usually node id "1")
    for node_id, node_data in workflow.items():
        if node_data.get("class_type") == "UGCVideoDownloader":
            node_data["inputs"]["url"] = video_url
    return workflow

def queue_prompt(workflow):
    """Queue a prompt in ComfyUI"""
    payload = {"prompt": workflow}
    response = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
    return response.json()

def check_status(prompt_id):
    """Check if a prompt is complete"""
    response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
    return response.json()

def automate_video_creation(video_url, workflow_path):
    """Fully automate video creation"""
    print(f"Starting automation for: {video_url}")

    # Load and update workflow
    workflow = load_workflow(workflow_path)
    workflow = update_workflow_url(workflow, video_url)

    # Queue the prompt
    result = queue_prompt(workflow)
    prompt_id = result["prompt_id"]

    print(f"Queued prompt: {prompt_id}")
    print("Waiting for completion...")

    # Wait for completion
    while True:
        status = check_status(prompt_id)
        if prompt_id in status:
            if status[prompt_id].get("status", {}).get("completed"):
                print("✓ Complete!")
                break
        time.sleep(10)

    return prompt_id

# Example usage
if __name__ == "__main__":
    video_urls = [
        "https://youtube.com/watch?v=VIDEO1",
        "https://youtube.com/watch?v=VIDEO2",
        "https://youtube.com/watch?v=VIDEO3",
    ]

    workflow_path = "ComfyUI/custom_nodes/ComfyUI-UGC-Video-Generator/workflows/03_complete_ugc_workflow.json"

    for url in video_urls:
        automate_video_creation(url, workflow_path)
        print(f"Finished processing: {url}\n")
```

#### 2. Run the automation

```bash
# Make sure ComfyUI is running
python automate_ugc.py
```

### Option 2: Batch Processing Script

Create `batch_process.py`:

```python
#!/usr/bin/env python3
"""
Batch process multiple videos
"""

import sys
sys.path.append('ComfyUI/custom_nodes/ComfyUI-UGC-Video-Generator')

from modules.video_downloader import VideoDownloader
from modules.script_extractor import ScriptExtractor
from modules.script_variation_generator import ScriptVariationGenerator
from modules.voice_generator import VoiceGenerator
from modules.avatar_generator import AvatarGenerator
import time

def process_video(url, num_variations=3):
    """Process a single video through the entire pipeline"""
    print(f"\n{'='*60}")
    print(f"Processing: {url}")
    print(f"{'='*60}\n")

    # 1. Download
    print("[1/5] Downloading video...")
    downloader = VideoDownloader()
    video_path = downloader.download(url)
    print(f"✓ Downloaded: {video_path}")

    # 2. Extract script
    print("\n[2/5] Extracting script...")
    extractor = ScriptExtractor(model_size='base')
    transcript = extractor.extract_script(video_path)
    script = transcript['text']
    print(f"✓ Script extracted ({len(script)} characters)")

    # 3. Generate variations
    print(f"\n[3/5] Generating {num_variations} variations...")
    script_gen = ScriptVariationGenerator()
    variations = script_gen.generate_variations(script, num_variations)
    script_gen.save_variations(variations, video_path.split('/')[-1].split('.')[0])
    print(f"✓ {len(variations)} variations generated")

    # 4. Generate voices
    print(f"\n[4/5] Generating voices...")
    voice_gen = VoiceGenerator()
    voices = ['male_1', 'female_1', 'male_energetic']
    audio_files = []

    for i, variation in enumerate(variations):
        voice = voices[i % len(voices)]
        audio_path = voice_gen.generate_audio(
            variation['script'],
            voice_name=voice,
            output_filename=f"variation_{i+1}.mp3"
        )
        if audio_path:
            audio_files.append(audio_path)
            print(f"✓ Voice {i+1} generated")

    # 5. Generate avatar videos
    print(f"\n[5/5] Generating avatar videos...")
    avatar_gen = AvatarGenerator(service='heygen')
    video_jobs = []

    for i, variation in enumerate(variations):
        result = avatar_gen.heygen_create_video(variation['script'])
        if result:
            video_id = result.get('video_id')
            video_jobs.append(video_id)
            print(f"✓ Avatar video {i+1} queued: {video_id}")

    print(f"\n{'='*60}")
    print(f"COMPLETE! Generated {len(variations)} variations")
    print(f"Audio files: {len(audio_files)}")
    print(f"Video jobs: {len(video_jobs)}")
    print(f"{'='*60}\n")

    return {
        'video_path': video_path,
        'variations': variations,
        'audio_files': audio_files,
        'video_jobs': video_jobs
    }

def batch_process(urls, variations_per_video=3, delay_between=30):
    """Process multiple videos with delay"""
    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n\nProcessing video {i}/{len(urls)}")

        try:
            result = process_video(url, variations_per_video)
            results.append(result)

            # Delay between videos to avoid rate limits
            if i < len(urls):
                print(f"\nWaiting {delay_between}s before next video...")
                time.sleep(delay_between)

        except Exception as e:
            print(f"\n✗ Error processing {url}: {e}")
            continue

    print(f"\n\n{'='*60}")
    print(f"BATCH COMPLETE!")
    print(f"Successfully processed: {len(results)}/{len(urls)} videos")
    print(f"{'='*60}")

    return results

if __name__ == "__main__":
    # Your list of videos to process
    video_urls = [
        "https://youtube.com/watch?v=VIDEO_ID_1",
        "https://youtube.com/watch?v=VIDEO_ID_2",
        "https://youtube.com/watch?v=VIDEO_ID_3",
    ]

    # Process them all
    batch_process(video_urls, variations_per_video=3, delay_between=30)
```

Run it:

```bash
python batch_process.py
```

## Scheduling & Batch Processing

### Option 1: Cron Job (Linux/Mac)

Create a daily automated job:

```bash
# Edit crontab
crontab -e

# Add this line to run every day at 2 AM
0 2 * * * cd /path/to/ComfyUI && /path/to/python batch_process.py >> /path/to/logs/ugc_automation.log 2>&1
```

### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\batch_process.py`

### Option 3: Watch Folder Automation

Create `watch_folder.py`:

```python
#!/usr/bin/env python3
"""
Watch a folder for new URL files and process them automatically
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class URLFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith('.txt'):
            print(f"New file detected: {event.src_path}")

            # Read URLs from file
            with open(event.src_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]

            # Process each URL
            for url in urls:
                print(f"Processing: {url}")
                process_video(url)

            # Move file to processed folder
            processed_path = event.src_path.replace('input', 'processed')
            os.rename(event.src_path, processed_path)
            print(f"Moved to: {processed_path}")

if __name__ == "__main__":
    watch_folder = "/path/to/input/folder"

    event_handler = URLFileHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()

    print(f"Watching folder: {watch_folder}")
    print("Drop .txt files with YouTube URLs to process automatically")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

## Production Automation Setup

### Complete Automated System

1. **Input Source** (choose one):
   - Watch folder for URL files
   - Web form that adds URLs to queue
   - API endpoint that accepts URLs
   - Scheduled scraper that finds videos

2. **Processing Queue**:
   - Store URLs in a database or file
   - Process one at a time
   - Retry failed jobs

3. **Output Handling**:
   - Auto-upload to YouTube
   - Send notifications when complete
   - Generate reports

### Example: Complete Automation System

Create `production_automation.py`:

```python
#!/usr/bin/env python3
"""
Production-ready automation system
"""

import json
import sqlite3
from datetime import datetime
import sys

class VideoQueue:
    def __init__(self, db_path='video_queue.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                added_date TEXT,
                processed_date TEXT,
                variations_count INTEGER,
                error TEXT
            )
        ''')
        self.conn.commit()

    def add_url(self, url):
        self.conn.execute(
            'INSERT INTO videos (url, added_date) VALUES (?, ?)',
            (url, datetime.now().isoformat())
        )
        self.conn.commit()

    def get_pending(self):
        cursor = self.conn.execute(
            'SELECT id, url FROM videos WHERE status = "pending"'
        )
        return cursor.fetchall()

    def mark_complete(self, video_id, variations_count):
        self.conn.execute(
            'UPDATE videos SET status = "complete", processed_date = ?, variations_count = ? WHERE id = ?',
            (datetime.now().isoformat(), variations_count, video_id)
        )
        self.conn.commit()

    def mark_failed(self, video_id, error):
        self.conn.execute(
            'UPDATE videos SET status = "failed", error = ? WHERE id = ?',
            (error, video_id)
        )
        self.conn.commit()

def process_queue():
    """Process all pending videos in the queue"""
    queue = VideoQueue()
    pending = queue.get_pending()

    print(f"Found {len(pending)} videos to process")

    for video_id, url in pending:
        print(f"\nProcessing video {video_id}: {url}")

        try:
            result = process_video(url)
            queue.mark_complete(video_id, len(result['variations']))
            print(f"✓ Complete!")
        except Exception as e:
            print(f"✗ Failed: {e}")
            queue.mark_failed(video_id, str(e))

if __name__ == "__main__":
    # Add videos to queue
    if len(sys.argv) > 1:
        queue = VideoQueue()
        for url in sys.argv[1:]:
            queue.add_url(url)
            print(f"Added to queue: {url}")

    # Process queue
    process_queue()
```

Usage:

```bash
# Add videos to queue
python production_automation.py "https://youtube.com/watch?v=VIDEO1" "https://youtube.com/watch?v=VIDEO2"

# Process queue (can be run by cron)
python production_automation.py
```

## Cost & Rate Limiting

### Managing API Costs

1. **Set Daily Limits**:
   - Max videos per day
   - Max API calls per day
   - Budget alerts

2. **Rate Limiting**:
   - Add delays between requests
   - Use exponential backoff
   - Queue systems

3. **Cost Optimization**:
   - Use smaller Whisper models (base instead of large)
   - Batch requests where possible
   - Cache common results

## Monitoring & Logging

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ugc_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Monitor System

1. Check logs regularly
2. Set up email alerts for failures
3. Monitor API usage and costs
4. Track success rates

## Next Steps

1. **Start Simple**: Test with 1-2 videos manually in ComfyUI
2. **Semi-Automate**: Use batch_process.py for small batches
3. **Full Automation**: Set up production system with queue
4. **Scale Up**: Add monitoring, error handling, and scheduling

## Support

For automation help:
- Check logs first
- Test with small batches
- Monitor API rate limits
- Review error messages

---

**You now have everything you need to fully automate UGC video creation!**
