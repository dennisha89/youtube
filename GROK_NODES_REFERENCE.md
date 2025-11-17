# Grok Workflow: Quick Node Reference

## Node Category Lookup Table

### VIDEO INPUT/OUTPUT NODES

| Node Name | Extension | Purpose | Key Inputs | Key Outputs |
|-----------|-----------|---------|-----------|------------|
| VHS_LoadVideo | VHS | Load video file | video_path, force_rate, frame_load_cap | VIDEO, frame_count |
| VHS_SplitVideo | VHS | Extract frames from video | VIDEO, force_size | IMAGE (sequence), frame_count |
| VHS_VideoCombine | VHS | Reassemble frames to video | images (IMAGE), frame_rate, format | VIDEO, frame_count |
| LoadAudio | Built-in | Load audio track | audio_path | AUDIO, sample_rate |
| VHS_AudioCombine | VHS | Attach audio to video | VIDEO, AUDIO | VIDEO |

---

### POSE/CONTROLNET NODES

| Node Name | Extension | Purpose | Key Inputs | Key Outputs |
|-----------|-----------|---------|-----------|------------|
| ControlNetLoader | Built-in/ComfyUI | Load ControlNet model | control_net_name (dropdown) | CONTROL_NET |
| OpenPose Preprocessor | Built-in | Extract skeleton from frame | IMAGE, include_body, include_hand | IMAGE (pose) |
| DWPreprocessor | Built-in | Prepare frame for ControlNet | IMAGE, resolution | IMAGE |
| ControlNetApply | Built-in | Apply pose control to generation | CONDITIONING, CONTROL_NET, IMAGE | CONDITIONING |

**ControlNet Model Path:** `ComfyUI/models/controlnet/control_openpose-fp16.safetensors`

---

### MODEL LOADING NODES

| Node Name | Extension | Purpose | Key Inputs | Key Outputs |
|-----------|-----------|---------|-----------|------------|
| CheckpointLoader | Built-in | Load Flux 1 Dev model | ckpt_name | MODEL, CLIP, VAE |
| LoraLoader | Built-in | Load style LoRA | lora_name, strength_model | MODEL, CLIP |
| UpscaleModelLoader | Built-in | Load upscale model | upscale_model_name | UPSCALE_MODEL |

**Model Paths:**
- Flux: `ComfyUI/models/diffusion_models/flux-1-dev.safetensors`
- Upscale: `ComfyUI/models/upscale_models/RealESRGAN_x4.pth`

---

### TEXT/PROMPT NODES

| Node Name | Extension | Purpose | Key Inputs | Key Outputs |
|-----------|-----------|---------|-----------|------------|
| CLIPTextEncode | Built-in | Encode text prompt to embeddings | text (STRING), CLIP | CONDITIONING |
| QwenImageEncoder | Qwen VL | Generate caption from image | IMAGE | caption (STRING), embedding |
| PrimitiveNode | Built-in | Input text/numbers/values | (manual input) | Any type |

---

### GENERATION NODES

| Node Name | Extension | Purpose | Key Inputs | Key Outputs |
|-----------|-----------|---------|-----------|------------|
| KSampler | Built-in | Generate image using diffusion | MODEL, CONDITIONING, steps, cfg | LATENT |
| VAEDecode | Built-in | Convert latent to image | LATENT, VAE | IMAGE |
| LatentUpscale | Built-in | Upscale latent (faster) | LATENT, width, height | LATENT |

---

### POST-PROCESSING NODES

| Node Name | Extension | Purpose | Key Inputs | Key Outputs |
|-----------|-----------|---------|-----------|------------|
| ImageUpscaleWithModel | Built-in | Upscale image with RealESRGAN | IMAGE, UPSCALE_MODEL | IMAGE |
| ImageColorCorrection | Built-in | Adjust colors | IMAGE, brightness, contrast, saturation | IMAGE |
| ImageDenoise | Built-in | Remove noise/artifacts | IMAGE, strength | IMAGE |
| GFPGAN | GFPGAN | Enhance faces | IMAGE, upscale | IMAGE |
| SaveImage | Built-in | Save frames | IMAGE, filename_prefix | - |

---

### UTILITY NODES

| Node Name | Purpose | Notes |
|-----------|---------|-------|
| Reroute | Organize connections | Visual routing only |
| Note | Add comments | Documentation |
| PrimitiveNode | Input values | Numbers, strings, dropdowns |

---

## Installation Commands

### VHS (Video Helper Suite)
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
cd ComfyUI-VideoHelperSuite
pip install -r requirements.txt
```

### Qwen VL (Optional)
```bash
pip install qwen-vl-utils transformers
```

### GFPGAN (Optional - Face Enhancement)
```bash
pip install gfpgan
```

---

## Model Download Links

### Required Models

| Model | Source | Destination | Size |
|-------|--------|-------------|------|
| Flux 1 Dev | [HuggingFace](https://huggingface.co/black-forest-labs/FLUX.1-dev) | `models/diffusion_models/` | 21.4 GB |
| Flux 1 Dev FP8 | [HuggingFace](https://huggingface.co/black-forest-labs/FLUX.1-dev) | `models/diffusion_models/` | 11.3 GB (recommended) |
| OpenPose ControlNet | [HuggingFace](https://huggingface.co/lllyasviel/control_v11p_openpose) | `models/controlnet/` | 2.1 GB |
| RealESRGAN x4 | [HuggingFace](https://huggingface.co/nayeemkhan/RealESRGAN_x4) | `models/upscale_models/` | 65 MB |

### Optional Models

| Model | Purpose | Source |
|-------|---------|--------|
| GFPGAN | Face enhancement | Built-in download |
| Various LoRAs | Style control | [CivitAI](https://civitai.com) |

---

## KSampler Configuration Quick Reference

### For Flux 1 Dev (Recommended Settings)

```
steps: 30-40
cfg: 3.5-4.5
sampler_name: "euler" or "dpmpp_2m"
scheduler: "karras" or "exponential"
denoise: 1.0
```

### Presets

**Fast (lower quality):**
```
steps: 20, cfg: 4.0
```

**Balanced (recommended):**
```
steps: 30, cfg: 4.0
```

**High Quality (slower):**
```
steps: 50, cfg: 3.5
```

---

## ControlNet Strength Configuration

| Scenario | Strength | start_percent | end_percent | Use Case |
|----------|----------|---------------|-------------|----------|
| Strong Control | 1.5 | 0.0 | 1.0 | Strict pose matching |
| Balanced (Recommended) | 1.0 | 0.0 | 0.8 | Good pose + generation quality |
| Subtle | 0.8 | 0.2 | 1.0 | Creative freedom with guidance |
| Minimal | 0.5 | 0.5 | 1.0 | Very creative, loose pose |

---

## Workflow Connection Checklist

### Minimal Working Workflow
- [ ] VHS_LoadVideo
- [ ] VHS_SplitVideo
- [ ] OpenPose Preprocessor
- [ ] CheckpointLoader (Flux 1 Dev)
- [ ] CLIPTextEncode
- [ ] ControlNetLoader
- [ ] ControlNetApply
- [ ] KSampler
- [ ] VAEDecode
- [ ] VHS_VideoCombine
- [ ] SaveImage

### Enhanced Workflow (Recommended)
- [ ] All minimal nodes plus:
- [ ] LatentUpscale
- [ ] ImageUpscaleWithModel (RealESRGAN)
- [ ] ImageColorCorrection
- [ ] ImageDenoise
- [ ] GFPGAN (optional)
- [ ] LoadAudio / VHS_AudioCombine

---

## Common Connection Patterns

### Pose Extraction Flow
```
Original Frame
  ↓
OpenPose Preprocessor (or DWPreprocessor)
  ↓
Pose Skeleton Image
  ↓
ControlNetApply (as control image)
```

### Text-to-Image Flow
```
Prompt String
  ↓
CLIPTextEncode
  ↓
CONDITIONING
  ↓
ControlNetApply (if using control)
  ↓
KSampler
```

### Image Generation Flow
```
KSampler
  ↓
LATENT
  ↓
LatentUpscale (optional)
  ↓
VAEDecode
  ↓
IMAGE
```

### Post-Processing Flow
```
Generated IMAGE
  ↓
ImageUpscaleWithModel
  ↓
ImageColorCorrection
  ↓
ImageDenoise (optional)
  ↓
GFPGAN (optional)
  ↓
Final IMAGE
```

### Video Reassembly Flow
```
Generated IMAGE Sequence ┐
                         ├→ VHS_VideoCombine
Original AUDIO ──────────┘
                         ↓
                    Final VIDEO
```

---

## Prompt Engineering Examples

### Professional/Corporate
```
"Professional headshot of a businesswoman in navy blazer, 
minimalist office background, studio lighting, 8K resolution, 
sharp focus, magazine quality photography"
```

### Lifestyle/Casual
```
"Natural lifestyle photo of woman in casual summer dress, 
bright outdoor setting with greenery, warm golden hour sunlight, 
vibrant colors, candid feel, high quality"
```

### High Fashion
```
"High fashion editorial photo of model in designer outfit, 
luxury boutique setting, dramatic lighting, cinematic composition, 
professional photography, premium quality, detailed"
```

### Consistency Prompt Format
```
[Subject Description] in [Setting], [Lighting], [Style], [Quality Descriptors]
```

---

## Hardware Performance Benchmarks

### On RTX 4090 (24GB VRAM)
- Per-frame time: 2-3 seconds
- Batch size: 1 (standard)
- Model: Flux 1 Dev (non-quantized)

### On RTX 3060 (12GB VRAM)
- Per-frame time: 8-10 seconds
- Batch size: 1
- Model: Flux 1 Dev FP8 (required)

### On RTX 4060 (8GB VRAM)
- Per-frame time: 15-20 seconds
- Batch size: 1
- Model: Flux 1 Dev FP8 + memory optimizations

---

## Troubleshooting Quick Guide

### Issue → Solution

| Issue | Solution |
|-------|----------|
| Node not found | Install extension (VHS, ControlNet) and restart ComfyUI |
| CUDA out of memory | Use FP8 model, reduce steps, smaller resolution |
| Pose not followed | Increase ControlNet strength to 1.2-1.5 |
| Bad image quality | Increase steps to 40-50, cfg to 4.5 |
| Audio out of sync | Verify frame rate matches input, use VHS_AudioCombine |
| Face distorted | Apply GFPGAN, add face detail to prompt |
| Color mismatch | Use ImageColorCorrection, adjust prompt for lighting |
| Slow generation | Use FP8 model, reduce resolution during testing |
| Models not downloading | Check HuggingFace auth, disk space, internet |

---

## File Paths Summary

```
ComfyUI/
├── models/
│   ├── diffusion_models/
│   │   ├── flux-1-dev.safetensors           (21.4 GB)
│   │   └── flux-1-dev-fp8.safetensors       (11.3 GB) ← USE THIS
│   ├── controlnet/
│   │   └── control_openpose-fp16.safetensors (2.1 GB)
│   ├── upscale_models/
│   │   └── RealESRGAN_x4.pth                (65 MB)
│   ├── loras/                               (optional LoRAs)
│   └── checkpoints/
│       └── gfpgan/                          (face restoration)
│
├── custom_nodes/
│   └── ComfyUI-VideoHelperSuite/            (VHS extension)
│
└── output/
    ├── videos/                              (final output)
    └── frames/                              (intermediate frames)
```

---

## Key Metrics to Monitor

### Generation Quality Factors
- **ControlNet Strength**: 0.8-1.5 (1.0 = balanced)
- **KSampler Steps**: 20-50 (30-40 recommended)
- **CFG Scale**: 3.5-4.5 (Flux is efficient)
- **Denoise**: 1.0 for full generation
- **Upscale**: RealESRGAN 2x or 4x

### Performance Factors
- **Frame Rate**: 24/30/60 FPS (match input)
- **Resolution**: 512x512 to 1024x1024
- **Batch Processing**: 1 frame at a time typical
- **Expected Time**: 2-20 seconds per frame

### Quality Checks
- [ ] Pose matched to original?
- [ ] Colors match original lighting?
- [ ] No artifacts/artifacts minimal?
- [ ] Face looks natural?
- [ ] Audio syncs with video?

---

## Production Workflow Template

```json
{
  "workflow_name": "Grok_Frame_Transform_Production",
  "stages": [
    {
      "name": "Input & Extraction",
      "nodes": ["VHS_LoadVideo", "VHS_SplitVideo", "LoadAudio"]
    },
    {
      "name": "Pose Analysis",
      "nodes": ["OpenPose Preprocessor"]
    },
    {
      "name": "Text Preparation",
      "nodes": ["PrimitiveNode (prompt)", "CLIPTextEncode"]
    },
    {
      "name": "Model Loading",
      "nodes": ["CheckpointLoader", "ControlNetLoader"]
    },
    {
      "name": "Generation",
      "nodes": ["ControlNetApply", "KSampler", "VAEDecode"]
    },
    {
      "name": "Enhancement",
      "nodes": ["ImageUpscaleWithModel", "ImageColorCorrection", "GFPGAN"]
    },
    {
      "name": "Assembly",
      "nodes": ["VHS_VideoCombine"]
    }
  ]
}
```

---

## Links & Resources

### Official Repos
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- VHS: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
- Flux 1 Dev: https://huggingface.co/black-forest-labs/FLUX.1-dev

### Models
- ControlNet: https://huggingface.co/lllyasviel/control_v11p_openpose
- RealESRGAN: https://huggingface.co/nayeemkhan/RealESRGAN_x4
- LoRAs: https://civitai.com

### Communities
- ComfyUI Discord: https://discord.gg/comfyui
- Stability AI Discord: https://discord.gg/stability-ai

---

*Last Updated: 2024*
*For latest information, check GROK_WORKFLOW_NODES.md*

