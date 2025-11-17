# Example Workflows

This directory contains example ComfyUI workflows for the UGC Video Generator nodes.

## Available Workflows

### 01_basic_script_extraction.json
**Purpose**: Download a video and extract/generate script variations

**Nodes Used**:
1. UGC Video Downloader - Download from YouTube
2. UGC Script Extractor - Transcribe with Whisper
3. UGC Script Variation Generator - Create variations

**Use Case**: Quick script extraction and variation generation

---

### 02_voice_generation.json
**Purpose**: Generate multiple voice versions from a script

**Nodes Used**:
1. UGC Text Input - Input your script
2. UGC Voice Generator (x2) - Generate male and female voices

**Use Case**: Testing different voices for your script

---

### 03_complete_ugc_workflow.json
**Purpose**: Complete end-to-end workflow from URL to final video

**Nodes Used**:
1. UGC Video Downloader - Download video
2. UGC Script Extractor - Extract script
3. UGC Script Variation Generator - Generate variations
4. UGC Variation Selector - Pick a specific variation
5. UGC Voice Generator - Generate voice
6. UGC Avatar Generator - Create avatar video
7. UGC Avatar Status Checker - Check processing status
8. UGC Avatar Downloader - Download final video

**Use Case**: Full production pipeline for creating UGC variations

---

## How to Use

### Loading a Workflow

1. Open ComfyUI
2. Click "Load" button
3. Navigate to `ComfyUI/custom_nodes/ComfyUI-UGC-Video-Generator/workflows/`
4. Select the workflow JSON file
5. Click "Load"

### Customizing Workflows

You can customize these workflows by:

- **Changing Parameters**: Edit node inputs directly in ComfyUI
- **Adding Nodes**: Right-click canvas → Add Node → UGC Video Generator
- **Connecting Nodes**: Drag from output to input to connect
- **Duplicating Nodes**: Select node and press Ctrl+C, Ctrl+V

### Tips

1. **Start Simple**: Begin with workflow 01 or 02
2. **Save Your Work**: Use "Save" to export your custom workflows
3. **Check Outputs**: Connect preview nodes to see intermediate results
4. **Handle Errors**: Check console output if nodes fail
5. **API Keys**: Make sure all API keys are set in `.env`

## Common Workflow Patterns

### Pattern 1: Multiple Variations in Parallel

```
Script Extractor
    ↓
Variation Generator
    ↓
    ├─→ Selector (0) → Voice (male_1) → Avatar
    ├─→ Selector (1) → Voice (female_1) → Avatar
    └─→ Selector (2) → Voice (male_2) → Avatar
```

### Pattern 2: A/B Testing Different Voices

```
Text Input
    ↓
    ├─→ Voice Generator (male_1)
    ├─→ Voice Generator (male_2)
    ├─→ Voice Generator (female_1)
    └─→ Voice Generator (female_2)
```

### Pattern 3: Batch Processing

```
Video Downloader (Video 1) → Script Extractor → Variations
Video Downloader (Video 2) → Script Extractor → Variations
Video Downloader (Video 3) → Script Extractor → Variations
```

## Troubleshooting

**Workflow won't load**: Make sure ComfyUI-UGC-Video-Generator is properly installed

**Nodes show errors**: Check that API keys are configured in `.env`

**Can't find nodes**: Restart ComfyUI after installation

**Outputs not visible**: Connect output to a preview or save node
