# Grok Workflow: Complete Implementation Guide

## Document Index

This collection provides comprehensive documentation for implementing the **Grok Video Transformation Workflow** using ComfyUI.

### Available Documents

1. **GROK_WORKFLOW_NODES.md** (Complete Reference)
   - Detailed node specifications
   - Input/output types for every node
   - Installation instructions for each extension
   - Configuration examples
   - Troubleshooting guide
   - **Start here for detailed information**

2. **GROK_NODES_REFERENCE.md** (Quick Lookup)
   - Node category lookup tables
   - Installation commands
   - Model download links
   - KSampler configuration presets
   - ControlNet strength settings
   - Hardware benchmarks
   - **Use this for quick reference during build**

3. **GROK_WORKFLOW_DIAGRAMS.md** (Visual Guide)
   - Complete architecture diagram
   - Step-by-step workflow visualization
   - Data type flow diagram
   - Processing pipeline stages
   - Configuration decision tree
   - Memory usage breakdown
   - **Reference while building the workflow**

4. **This Document** (Implementation Guide)
   - Overview and quick start
   - Step-by-step installation
   - Building the workflow
   - Testing and optimization
   - **Start here for first-time implementation**

---

## Quick Overview: What is Grok Workflow?

The Grok Workflow is a frame-by-frame video transformation system that:

1. **Extracts** video frames and audio
2. **Analyzes** pose/skeleton from each frame
3. **Generates** new images with:
   - New appearance (different person/look)
   - Original pose (same movements preserved)
   - Custom styling (controlled by text prompts)
4. **Reassembles** frames into final video with original audio

### Key Difference from Avatar-Based Approach
- Avatar services (HeyGen, D-ID) replace entire video
- Grok workflow transforms appearance while keeping movement
- Uses **Flux 1 Dev** + **ControlNet** for precise control

---

## System Requirements

### Hardware Requirements

**Minimum:**
- GPU: 12GB VRAM (RTX 3060, RTX 4060, A4000)
- CPU: 8+ cores
- RAM: 16GB system memory
- Storage: 50GB+ (for models)
- Processing time: ~5-10 seconds per frame

**Recommended:**
- GPU: 24GB+ VRAM (RTX 4090, A100)
- CPU: 16+ cores
- RAM: 32GB system memory
- Storage: 100GB+ (for models + working files)
- Processing time: ~2-3 seconds per frame

### Software Requirements

- ComfyUI (latest)
- Python 3.10+
- CUDA 11.8+ or ROCm (for AMD)
- FFmpeg (for video I/O)

---

## Step 1: Install ComfyUI

If you don't have ComfyUI installed:

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Run ComfyUI
python main.py
# Open http://127.0.0.1:8188 in browser
```

---

## Step 2: Install Required Extensions

### Install Video Helper Suite (VHS)

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
cd ComfyUI-VideoHelperSuite
pip install -r requirements.txt
cd ../..
```

### Verify ControlNet Support

ComfyUI should have ControlNet built-in. If not:

```bash
# Most modern ComfyUI versions have this built-in
# No additional installation needed
```

### Optional: Qwen VL (for dynamic prompts)

```bash
pip install qwen-vl-utils transformers
```

### Optional: GFPGAN (for face enhancement)

```bash
pip install gfpgan
```

---

## Step 3: Download Required Models

### Create Model Directories

```bash
cd ComfyUI/models

# Create subdirectories if they don't exist
mkdir -p diffusion_models
mkdir -p controlnet
mkdir -p upscale_models
```

### Download Flux 1 Dev Model

**Important:** Use the FP8 (quantized) version to save VRAM

```bash
# Using huggingface-cli (recommended)
pip install huggingface-hub

huggingface-cli download black-forest-labs/FLUX.1-dev \
  --include "flux1-dev-Q4_0.gguf" "flux1-dev.safetensors" \
  --local-dir ComfyUI/models/diffusion_models/

# Or download manually from:
# https://huggingface.co/black-forest-labs/FLUX.1-dev
```

**File:** `flux-1-dev-fp8.safetensors` (11.3 GB)
**Location:** `ComfyUI/models/diffusion_models/`

### Download OpenPose ControlNet

```bash
huggingface-cli download lllyasviel/control_v11p_openpose \
  --include "diffusion_pytorch_model.fp16.safetensors" \
  --local-dir ComfyUI/models/controlnet/
```

**File:** `control_openpose-fp16.safetensors` (2.1 GB)
**Location:** `ComfyUI/models/controlnet/`

### Download RealESRGAN Upscaler

```bash
huggingface-cli download nayeemkhan/RealESRGAN_x4 \
  --include "RealESRGAN_x4.pth" \
  --local-dir ComfyUI/models/upscale_models/
```

**File:** `RealESRGAN_x4.pth` (65 MB)
**Location:** `ComfyUI/models/upscale_models/`

### Verify Model Downloads

```bash
ls -lah ComfyUI/models/diffusion_models/    # Should see flux models
ls -lah ComfyUI/models/controlnet/           # Should see controlnet
ls -lah ComfyUI/models/upscale_models/       # Should see RealESRGAN
```

---

## Step 4: Create Test Workflow

Start in ComfyUI UI by creating nodes manually or importing JSON.

### Minimal Test Workflow (Single Frame)

1. **Add VHS_LoadVideo**
   - Set video path to your test video

2. **Add VHS_SplitVideo**
   - Connect VIDEO output from VHS_LoadVideo
   - Set force_size to keep original

3. **Add OpenPose Preprocessor**
   - Connect IMAGE output from VHS_SplitVideo
   - Set include_body: true, hands/face: false

4. **Add CheckpointLoader**
   - ckpt_name: "flux-1-dev-fp8.safetensors"

5. **Add ControlNetLoader**
   - control_net_name: "control_openpose-fp16"

6. **Add CLIPTextEncode**
   - text: "professional woman in office, photography"
   - clip: from CheckpointLoader

7. **Add ControlNetApply**
   - conditioning: from CLIPTextEncode
   - control_net: from ControlNetLoader
   - image: from OpenPose Preprocessor
   - strength: 1.0

8. **Add KSampler**
   - model: from CheckpointLoader
   - positive: from ControlNetApply
   - negative: "blurry, distorted, artifacts"
   - steps: 30
   - cfg: 4.0

9. **Add VAEDecode**
   - samples: from KSampler
   - vae: from CheckpointLoader

10. **Add SaveImage**
    - images: from VAEDecode

11. **Queue and Run**
    - Click "Queue Prompt"
    - Monitor console for progress
    - Check output folder for generated image

---

## Step 5: Enhanced Workflow (Production Ready)

Add these nodes after VAEDecode for better quality:

### Upscaling
- **ImageUpscaleWithModel**
  - upscale_model: "RealESRGAN_x4"
  - image: from VAEDecode

### Color Correction
- **ImageColorCorrection**
  - image: from ImageUpscaleWithModel
  - brightness: 0.0 (adjust if needed)
  - contrast: 1.0
  - saturation: 1.0

### Denoising (Optional)
- **ImageDenoise**
  - image: from ImageColorCorrection
  - strength: 0.3-0.5

### Face Enhancement (Optional)
- **GFPGAN**
  - image: from ImageDenoise
  - upscale: 2

### Audio & Video Assembly

1. **LoadAudio**
   - audio_path: same as input video

2. **VHS_VideoCombine**
   - images: from SaveImage output (collect all frames)
   - frame_rate: 24 (match input)
   - format: "video/h264-mp4"

3. **VHS_AudioCombine**
   - video: from VHS_VideoCombine
   - audio: from LoadAudio

---

## Step 6: Configuration Tuning

### Adjust ControlNet Strength

**For strict pose matching:**
```
strength: 1.5
start_percent: 0.0
end_percent: 1.0
```

**For balanced (recommended):**
```
strength: 1.0
start_percent: 0.0
end_percent: 0.8
```

**For creative freedom:**
```
strength: 0.8
start_percent: 0.2
end_percent: 1.0
```

### Adjust KSampler Parameters

**For speed:**
```
steps: 20
cfg: 4.0
sampler: "euler"
scheduler: "karras"
```

**For quality (recommended):**
```
steps: 30-40
cfg: 4.0
sampler: "euler" or "dpmpp_2m"
scheduler: "karras"
```

**For best quality (slower):**
```
steps: 50
cfg: 3.5
sampler: "dpmpp_2m"
scheduler: "exponential"
```

### Optimize for Your Hardware

**RTX 4090 (24GB):**
- Use full: `flux-1-dev.safetensors`
- steps: 40, cfg: 4.0
- Per-frame time: 3-5s

**RTX 3060 (12GB):**
- Use FP8: `flux-1-dev-fp8.safetensors`
- steps: 30, cfg: 4.0
- Per-frame time: 8-10s

**RTX 4060 (8GB):**
- Use FP8: `flux-1-dev-fp8.safetensors`
- steps: 20, cfg: 4.0
- Resolution: 512x512
- Per-frame time: 15-20s

---

## Step 7: Test and Debug

### Test Single Frame First

1. In ComfyUI, load test workflow
2. Set `frame_load_cap: 1` in VHS_LoadVideo
3. Run just pose extraction to verify skeleton detection
4. Run full generation pipeline on 1 frame
5. Check output quality before batch processing

### Common Issues

**Issue:** CUDA out of memory
- Solution: Use FP8 model, reduce steps, smaller resolution

**Issue:** Pose not detected
- Solution: Check OpenPose output, may need to adjust image

**Issue:** Poor image quality
- Solution: Increase steps to 40-50, improve prompt

**Issue:** Face looks distorted
- Solution: Add GFPGAN, increase prompt detail for face

**Issue:** Colors don't match
- Solution: Use ImageColorCorrection, sample colors from original

---

## Step 8: Batch Processing Setup

### For Multiple Frames

Create Python script `grok_batch_processor.py`:

```python
#!/usr/bin/env python3

import requests
import json
import time

COMFYUI_URL = "http://127.0.0.1:8188"

def queue_workflow(workflow_json):
    """Send workflow to ComfyUI"""
    response = requests.post(
        f"{COMFYUI_URL}/prompt",
        json={"prompt": workflow_json}
    )
    return response.json()["prompt_id"]

def check_status(prompt_id):
    """Check workflow execution status"""
    response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
    history = response.json()
    return prompt_id in history

def process_video(video_path, num_frames=10):
    """
    Process video frame by frame
    
    1. Load workflow template
    2. For each frame:
       - Update video path and frame index
       - Queue to ComfyUI
       - Wait for completion
       - Collect output image
    3. Reassemble with audio
    """
    
    # Load your workflow JSON
    with open("grok_workflow.json") as f:
        workflow = json.load(f)
    
    for frame_idx in range(num_frames):
        print(f"Processing frame {frame_idx + 1}/{num_frames}...")
        
        # Update workflow (adjust based on your node IDs)
        workflow["1"]["inputs"]["video"] = video_path
        
        # Queue and wait
        prompt_id = queue_workflow(workflow)
        
        # Poll for completion
        while not check_status(prompt_id):
            time.sleep(2)
        
        print(f"  Frame {frame_idx + 1} complete")
    
    print("All frames processed!")

if __name__ == "__main__":
    process_video("input_video.mp4", num_frames=24)
```

---

## Step 9: Verification Checklist

Before deploying to production:

- [ ] Single frame test passes
- [ ] Pose extraction working correctly
- [ ] Generated images match prompt
- [ ] Color correction applied
- [ ] Face enhancement (if enabled) looks good
- [ ] Multiple frames processed successfully
- [ ] Audio syncs with video frames
- [ ] Output file plays correctly
- [ ] File size reasonable
- [ ] Processing time acceptable

---

## Performance Optimization Tips

### Speed Optimizations

1. **Use FP8 Model**
   - `flux-1-dev-fp8.safetensors` instead of full precision
   - Saves ~10GB VRAM, minimal quality loss

2. **Reduce Steps**
   - Start at 20-25 instead of 40
   - Flux is efficient with low steps

3. **Lower Resolution During Testing**
   - Generate at 512x512, upscale after
   - Faster generation, same final quality

4. **Batch Processing**
   - Process multiple frames in parallel on multiple GPUs
   - Or sequential with careful memory management

### Quality Optimizations

1. **Increase Steps Strategically**
   - Use steps: 40-50 for final render
   - Steps: 20-25 for preview

2. **Better Prompts**
   - Detailed prompts > high steps
   - Specific clothing, lighting, setting

3. **ControlNet Tuning**
   - strength: 1.0-1.2 for balanced results
   - end_percent: 0.8 allows creative variation

4. **Post-Processing**
   - Always use ImageUpscaleWithModel
   - GFPGAN for face-heavy content
   - ImageColorCorrection to match original

---

## Common Workflows

### Professional Headshots

```
Prompt: "Professional headshot, woman in business suit, 
studio background, perfect lighting, sharp focus, 
magazine quality, 8K resolution"

ControlNet strength: 1.0
Steps: 35
CFG: 4.0
Add: GFPGAN for face enhancement
```

### Lifestyle/Casual

```
Prompt: "Natural candid photo, woman in casual clothing, 
outdoor setting, golden hour sunlight, warm colors, 
lifestyle photography, vibrant"

ControlNet strength: 0.9
Steps: 30
CFG: 4.0
Skip: GFPGAN (natural look)
```

### Fashion/High-Style

```
Prompt: "High fashion editorial, woman in designer outfit, 
luxury boutique, dramatic lighting, cinematic, 
premium quality, professional photography"

ControlNet strength: 0.8
Steps: 40
CFG: 3.5
Add: GFPGAN for detail
Use: Professional photography LoRA (optional)
```

---

## Troubleshooting Guide

### Model Loading Issues

**Error:** "Model not found"
- Check file exists in correct directory
- Verify filename spelling
- Restart ComfyUI

**Error:** "CUDA out of memory"
- Use FP8 quantized version
- Reduce image resolution
- Reduce step count
- Close other GPU applications

### Generation Issues

**Error:** "Pose not detected"
- Check input video quality
- Ensure person is clearly visible
- Try DWPreprocessor instead of OpenPose

**Error:** "Bad generation quality"
- Improve prompt (be more specific)
- Increase step count
- Increase CFG scale
- Use LoRA for style consistency

**Error:** "Audio out of sync"
- Verify frame rate matches input
- Check frame count = fps × audio duration
- Use VHS_AudioCombine (not manual mux)

### Workflow Issues

**Error:** "Node not found"
- Install missing extension
- Restart ComfyUI after installation

**Error:** "Type mismatch"
- Verify output type matches input type
- IMAGE → IMAGE
- CONDITIONING → CONDITIONING
- etc.

---

## Next Steps

1. **Install and Setup** (30 min)
   - Follow Steps 1-3 above

2. **Build Minimal Workflow** (1 hour)
   - Create test workflow from Step 4

3. **Test Single Frame** (30 min)
   - Verify all nodes work
   - Check pose extraction
   - Review generated image

4. **Enhance with Post-Processing** (30 min)
   - Add upscaler, color correction, etc.

5. **Batch Process Test Video** (2-4 hours)
   - Process 10-20 frames
   - Monitor for issues

6. **Production Deployment** (ongoing)
   - Process full videos
   - Optimize settings
   - Monitor results

---

## Resources

### Documentation
- Full node reference: GROK_WORKFLOW_NODES.md
- Quick lookup: GROK_NODES_REFERENCE.md
- Visual diagrams: GROK_WORKFLOW_DIAGRAMS.md

### External Links
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- VHS: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
- Flux 1 Dev: https://huggingface.co/black-forest-labs/FLUX.1-dev
- ControlNet: https://huggingface.co/lllyasviel/control_v11p_openpose

### Communities
- ComfyUI Discord: https://discord.gg/comfyui
- Stability AI Discord: https://discord.gg/stability-ai

---

## Support & Debugging

### Enable Verbose Logging

```bash
# Run ComfyUI with debug output
python main.py --verbose
```

### Check System Resources

```bash
# Monitor GPU usage (NVIDIA)
watch -n 1 nvidia-smi

# Check disk space
df -h

# Check RAM usage
free -h
```

### Test Individual Components

Test each stage independently:
1. Video loading (VHS_LoadVideo)
2. Frame extraction (VHS_SplitVideo)
3. Pose detection (OpenPose)
4. Prompt encoding (CLIPTextEncode)
5. Image generation (KSampler)
6. Post-processing (Upscale, etc.)
7. Video assembly (VHS_VideoCombine)

---

## Final Notes

- Start simple, add complexity gradually
- Test with short videos first (10-30 seconds)
- Monitor VRAM usage, adjust settings if needed
- Save successful workflow configurations
- Document your prompt library
- Back up generated assets

**Happy transforming!**

