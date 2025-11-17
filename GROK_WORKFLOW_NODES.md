# Grok Workflow: ComfyUI Nodes & Extensions Guide

## Overview

This document outlines all ComfyUI nodes and extensions required for the **Grok Workflow** - a frame-by-frame video transformation pipeline that:

- Takes input video
- Extracts frames + audio
- Transforms each frame (new person/background) while keeping poses
- Reassembles into video with synced audio

This is different from avatar-based generation. Instead, we use **Flux 1 Dev** with **ControlNet** to generate new appearances while preserving pose/movement.

---

## 1. VIDEO HELPER SUITE (VHS)

### Purpose
Load videos, extract frames, save frames, and reassemble video.

### Extension Install
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
pip install -r ComfyUI-VideoHelperSuite/requirements.txt
```

### Required Nodes

#### 1.1 VHS_VideoCombine
**Purpose**: Reassemble video from frames

**Input Types:**
- `images` (IMAGE) - Frame sequence
- `frame_rate` (INT) - FPS (default: 24)
- `loop_count` (INT) - Number of loops (default: 0)
- `filename_prefix` (STRING) - Output filename
- `format` (["video/h264-mp4", "video/h265-mp4", "video/webm"]) - Format
- `crf` (INT) - Quality 0-51 (default: 23, lower = better)

**Outputs:**
- `VIDEO` (VIDEO) - Encoded video file
- `frame_count` (INT) - Total frames processed

**File Output**: Saved to `ComfyUI/output/`

#### 1.2 VHS_LoadVideo
**Purpose**: Load video files

**Input Types:**
- `video` (STRING) - Video file path
- `force_rate` (INT) - Override frame rate (0 = auto)
- `force_size` (STRING) - Resize to WxH ("" = keep original)
- `custom_width` (INT) - Custom width
- `custom_height` (INT) - Custom height
- `frame_load_cap` (INT) - Max frames to load (0 = all)
- `skip_first_frames` (INT) - Frames to skip
- `select_every_nth` (INT) - Sample every Nth frame

**Outputs:**
- `VIDEO` (VIDEO) - Video sequence
- `frame_count` (INT) - Number of frames loaded

#### 1.3 VHS_SplitVideo
**Purpose**: Extract frames from video

**Input Types:**
- `video` (VIDEO) - Input video from VHS_LoadVideo
- `force_size` (STRING) - Size override
- `custom_width` (INT) - Width in pixels
- `custom_height` (INT) - Height in pixels

**Outputs:**
- `IMAGE` (IMAGE) - Frame sequence
- `frame_count` (INT) - Total frames

#### 1.4 VHS_VideoCombine (Alternative: Video to Frames Conversion)
**For extracting audio:**
- Extracts frame sequence AND audio track separately

**Key Configuration:**
```
frame_rate: Match original video (24/30/60)
```

---

## 2. AUDIO PROCESSING NODES

### 2.1 Audio Load Node (Built-in ComfyUI)

**Node Name:** `LoadAudio` / `VHS_LoadAudio`

**Purpose**: Load audio from video or audio file

**Input Types:**
- `audio_path` (STRING) - Path to audio file or video with audio track

**Outputs:**
- `AUDIO` (AUDIO) - Audio data
- `sample_rate` (INT) - Sample rate in Hz
- `duration` (FLOAT) - Duration in seconds

### 2.2 Audio Info Node

**Purpose**: Get audio metadata

**Outputs:**
- `duration` (FLOAT) - Length in seconds
- `sample_rate` (INT) - Hz
- `channels` (INT) - Mono/Stereo
- `frame_count` (INT) - Total audio samples

### 2.3 VHS_AudioCombine (Audio Reattachment)

**Purpose**: Sync extracted audio back to video

**Input Types:**
- `video` (VIDEO) - Video frames (without audio)
- `audio` (AUDIO) - Audio track
- `filename_prefix` (STRING) - Output filename

**Outputs:**
- `VIDEO` (VIDEO) - Video with audio attached

**Important:** This is CRUCIAL for final video reassembly with original audio

---

## 3. CONTROLNET NODES

### Purpose
Extract and control pose information through video frames.

### Extension Install
```bash
# Standard ControlNet support (built-in to many ComfyUI versions)
# Or explicit: comfyui-controlnet-nodes
```

### Required Nodes

#### 3.1 ControlNetLoader
**Purpose**: Load ControlNet model (OpenPose)

**Input Types:**
- `control_net_name` (STRING dropdown) - Model selection:
  - `control_openpose-fp16.safetensors` ← **Use this for pose**
  - `control_canny-fp16.safetensors` (edge detection - alternative)
  - `control_depth-fp16.safetensors` (depth - alternative)

**Outputs:**
- `CONTROL_NET` (CONTROLNET) - Loaded model

#### 3.2 ControlNetLoader Location
```
ComfyUI/models/controlnet/
# Download from: https://huggingface.co/lllyasviel/control_v11p_openpose
```

#### 3.3 DWPreprocessor (Frame Preprocessing)
**Purpose**: Prepare frames for ControlNet (OpenPose detection)

**Input Types:**
- `image` (IMAGE) - Input frame
- `resolution` (INT) - Target resolution (512, 768, 1024)

**Outputs:**
- `IMAGE` (IMAGE) - Processed image with pose skeleton overlay

#### 3.4 OpenPose Preprocessor Node
**Purpose**: Extract skeleton/pose information from frame

**Input Types:**
- `image` (IMAGE) - Input frame
- `include_body` (BOOLEAN) - Extract body pose (default: True)
- `include_hand` (BOOLEAN) - Extract hand details (default: False)
- `include_face` (BOOLEAN) - Extract facial keypoints (default: False)

**Outputs:**
- `IMAGE` (IMAGE) - Frame with pose skeleton drawn

**Pose Format:**
- 17 keypoints for body (COCO format):
  - Head, shoulders, elbows, wrists
  - Hips, knees, ankles
- Each keypoint has (x, y, confidence)

---

## 4. FLUX 1 DEV IMAGE GENERATION

### Purpose
Generate new images with new person/background while using ControlNet to preserve pose.

### Extension Install
```bash
# Flux model (requires huggingface-hub)
pip install huggingface-hub

# Download Flux 1 Dev to:
ComfyUI/models/diffusion_models/
```

### Required Nodes

#### 4.1 CheckpointLoader
**Purpose**: Load Flux 1 Dev model

**Input Types:**
- `ckpt_name` (STRING dropdown) - Model:
  - `flux-1-dev.safetensors` ← **Flux 1 Dev (non-quantized)**
  - `flux-1-dev-fp8.safetensors` ← **Memory-efficient version**

**Outputs:**
- `MODEL` (MODEL) - Loaded model
- `CLIP` (CLIP) - Text encoder
- `VAE` (VAE) - Image encoder/decoder

#### 4.2 CLIPTextEncode
**Purpose**: Convert text prompts to embeddings

**Input Types:**
- `text` (STRING) - Prompt text
- `clip` (CLIP) - From CheckpointLoader

**Outputs:**
- `CONDITIONING` (CONDITIONING) - Text embeddings

**Example Prompt Structure:**
```
"A professional woman in business attire, standing in modern office, warm lighting, 
high quality, 8k resolution, detailed face, professional photography"
```

#### 4.3 LoraLoader (Optional - for style control)
**Purpose**: Load LoRA adapters for consistent styling

**Input Types:**
- `lora_name` (STRING) - LoRA file
- `strength_model` (FLOAT) - 0.0-2.0 (recommended: 0.8-1.2)
- `strength_clip` (FLOAT) - 0.0-2.0

**Outputs:**
- `MODEL` (MODEL) - LoRA-modified model
- `CLIP` (CLIP) - LoRA-modified CLIP

**Useful LoRAs:**
- Professional photography
- Cinematic quality
- Specific art styles

#### 4.4 ControlNetApply
**Purpose**: Apply ControlNet to guide generation

**Input Types:**
- `conditioning` (CONDITIONING) - From CLIPTextEncode
- `control_net` (CONTROLNET) - From ControlNetLoader
- `image` (IMAGE) - Pose reference (OpenPose output)
- `strength` (FLOAT) - Control strength (0.0-2.0, recommend: 1.0-1.5)
- `start_percent` (FLOAT) - When to start guidance (0.0-1.0)
- `end_percent` (FLOAT) - When to end guidance (0.0-1.0)

**Outputs:**
- `CONDITIONING` (CONDITIONING) - Modified conditioning with control

**Connection Flow:**
```
OpenPose Output → ControlNetApply
TextEncode Output → ControlNetApply
ControlNetLoader → ControlNetApply
```

#### 4.5 KSampler (Core Generation)
**Purpose**: Generate image using model + conditioning

**Input Types:**
- `model` (MODEL) - From CheckpointLoader
- `positive` (CONDITIONING) - From ControlNetApply
- `negative` (CONDITIONING) - Negative prompt embeddings
- `latent_image` (LATENT) - Starting latent
- `seed` (INT) - Random seed
- `steps` (INT) - Denoising steps (20-50 for Flux)
- `cfg` (FLOAT) - Guidance scale (1.0-8.0, Flux: 3.5-4.5)
- `sampler_name` (STRING) - "euler", "dpmpp_2m", "heun", etc.
- `scheduler` (STRING) - "normal", "karras", "exponential"
- `denoise` (FLOAT) - 0.0-1.0 (1.0 = full generation, 0.5 = img2img blend)

**Outputs:**
- `LATENT` (LATENT) - Generated latent representation

#### 4.6 VAEDecode
**Purpose**: Convert latent to image

**Input Types:**
- `samples` (LATENT) - From KSampler
- `vae` (VAE) - From CheckpointLoader

**Outputs:**
- `IMAGE` (IMAGE) - Generated image (512x512 or higher)

---

## 5. QWEN IMAGE ENCODER (Optional - for Image Analysis)

### Purpose
Encode/caption images for better prompt generation and image understanding.

### Extension Install
```bash
pip install qwen-vl-utils transformers torch pillow
```

### Nodes

#### 5.1 QwenImageEncoder
**Purpose**: Analyze image and generate detailed captions

**Input Types:**
- `image` (IMAGE) - Input frame to analyze
- `model` (STRING) - "qwen-vl-max" or "qwen-vl"

**Outputs:**
- `caption` (STRING) - Generated description
- `embedding` (EMBEDDING) - Image embedding

**Use Case:**
- Analyze original video frame to extract context
- Generate dynamic prompts based on frame content
- Maintain consistency in transformations

**Example Workflow:**
```
Original Frame → QwenImageEncoder → Caption
Caption → (enhance with additional style prompt) → CLIPTextEncode
```

---

## 6. IMAGE PROCESSING NODES

### Purpose
Prepare and enhance generated images

#### 6.1 LatentUpscale
**Purpose**: Enlarge latent before decoding (faster than post-decode upscaling)

**Input Types:**
- `samples` (LATENT) - From KSampler
- `upscale_method` (STRING) - "nearest", "linear", "lanczos"
- `width` (INT) - Target width
- `height` (INT) - Target height

**Outputs:**
- `LATENT` (LATENT) - Upscaled latent

#### 6.2 ImageUpscaleWithModel
**Purpose**: Post-decode upscaling with model

**Input Types:**
- `upscale_model` (UPSCALE_MODEL) - From UpscaleModelLoader
- `image` (IMAGE) - From VAEDecode

**Outputs:**
- `IMAGE` (IMAGE) - Upscaled image (2x, 4x, etc.)

---

## 7. POST-PROCESSING NODES

### Purpose
Enhance and refine generated images

### 7.1 Upscale Nodes

#### RealESRGAN Upscaler
**Node Name:** `UpscaleModelLoader` + `ImageUpscaleWithModel`

**Models Available:**
- `RealESRGAN_x2` - 2x upscale
- `RealESRGAN_x4` - 4x upscale (for final output)
- `RealESRGAN_x4_anime` - Anime-optimized

**Input Types:**
- `image` (IMAGE) - Generated frame
- `upscale_model` (STRING) - Model selection

**Outputs:**
- `IMAGE` (IMAGE) - Upscaled result

### 7.2 Color/Tone Adjustments

#### ImageAdjustment / ImageColorCorrection
**Purpose:** Match original video color grading

**Input Types:**
- `image` (IMAGE) - Generated frame
- `brightness` (FLOAT) - -1.0 to 1.0
- `contrast` (FLOAT) - -1.0 to 1.0
- `saturation` (FLOAT) - -1.0 to 1.0
- `hue_shift` (INT) - -180 to 180 degrees

**Outputs:**
- `IMAGE` (IMAGE) - Color-corrected image

### 7.3 Denoise Nodes

#### ImageDenoise / LatentDenoise
**Purpose:** Reduce artifacts

**Input Types:**
- `image` (IMAGE) - Noisy frame
- `strength` (FLOAT) - 0.0-1.0 (recommended: 0.3-0.5)

**Outputs:**
- `IMAGE` (IMAGE) - Denoised image

### 7.4 Face Enhancement (Optional)

#### GFPGAN Face Restoration
**Purpose:** Enhance facial details

**Extension:**
```bash
pip install gfpgan
```

**Input Types:**
- `image` (IMAGE) - Frame with face
- `bg_upscale` (INT) - Background upscale 1-4x
- `upscale` (INT) - Face upscale 1-4x

**Outputs:**
- `IMAGE` (IMAGE) - Enhanced face

---

## 8. UTILITY NODES

### 8.1 Reroute
**Purpose:** Organize workflow connections

### 8.2 Note
**Purpose:** Add comments to workflow

### 8.3 PrimitiveNode
**Purpose:** Input numbers/strings/selections

### 8.4 SaveImage
**Purpose:** Save individual frames (for debugging)

**Input Types:**
- `images` (IMAGE) - Frames to save
- `filename_prefix` (STRING) - Filename

---

## COMPLETE WORKFLOW CONNECTION DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                    GROK WORKFLOW - FULL PIPELINE                 │
└─────────────────────────────────────────────────────────────────┘

STAGE 1: INPUT & EXTRACTION
────────────────────────────
[Input Video]
      ↓
[VHS_LoadVideo] → [VHS_SplitVideo] ┐
                                    ├→ [IMAGE] Frames
                                    │
[VHS_VideoExtractAudio] → [AUDIO] Audio Track


STAGE 2: POSE EXTRACTION (Per Frame)
──────────────────────────────────────
[Original Frame] → [OpenPose Preprocessor] → [Pose Skeleton Image]
      ↓
[DWPreprocessor] → [Control Reference]


STAGE 3: TEXT PROMPT GENERATION
───────────────────────────────
Option A (Static Prompt):
[Prompt String] → [CLIPTextEncode] → [CONDITIONING]

Option B (Dynamic - with Qwen):
[Original Frame] → [QwenImageEncoder] → [Caption String]
                                               ↓
                                        [Enhanced Prompt]
                                               ↓
                                        [CLIPTextEncode] → [CONDITIONING]


STAGE 4: LOAD MODELS
────────────────────
[CheckpointLoader] → [Flux 1 Dev Model]
                     [CLIP Encoder]
                     [VAE Encoder/Decoder]
                                 ↓
                         [LoraLoader] (optional)


STAGE 5: CONTROLNET APPLICATION
────────────────────────────────
[ControlNetLoader] (OpenPose model)
      ↓
[ControlNetApply] ← [CONDITIONING] (from Step 3)
      ↓              ← [Pose Skeleton] (from Step 2)
[Modified CONDITIONING]


STAGE 6: IMAGE GENERATION
──────────────────────────
[Flux Model] ←─ [Modified Conditioning]
[CLIP] ←────────── [KSampler]
[VAE] ←───────────────↓
                  [Latent Output]
                       ↓
                  [LatentUpscale] (optional)
                       ↓
                  [VAEDecode]
                       ↓
                  [Generated Image]


STAGE 7: POST-PROCESSING
────────────────────────
[Generated Image] → [ImageUpscaleWithModel] (RealESRGAN 4x)
                         ↓
                 [ImageColorCorrection] (match original video)
                         ↓
                 [ImageDenoise] (optional)
                         ↓
                 [GFPGAN] (face enhancement, optional)
                         ↓
                 [Final Enhanced Frame]


STAGE 8: VIDEO REASSEMBLY
──────────────────────────
[Final Frames Sequence] ┐
                        ├→ [VHS_VideoCombine] ← [Frame Rate: 24/30/60]
[Audio Track] ──────────┘        ↓
                         [Video with Audio]
                                 ↓
                         [SaveVideo Output]

```

---

## CONFIGURATION EXAMPLES

### Example Prompt Structures

#### Professional Transformation
```
"High-quality professional headshot, woman in navy business suit, 
modern office background, natural lighting, 8K resolution, detailed 
facial features, professional photography style, sharp focus"
```

#### Casual/Lifestyle
```
"Natural candid photo of woman in casual clothing, bright sunny day, 
outdoor park setting, warm golden hour lighting, vibrant colors, 
lifestyle photography, professional quality"
```

#### Consistent Style Across Frames
Use LoRA: `film_noir_style.safetensors`
```
"Film noir aesthetic, dramatic shadows, vintage black and white, 
woman detective in 1940s style clothing, moody atmosphere, 
cinematic lighting"
```

### ControlNet Strength Settings

**For Strong Pose Control:**
```
strength: 1.5
start_percent: 0.0
end_percent: 1.0
```

**For Balanced Generation:**
```
strength: 1.0
start_percent: 0.0
end_percent: 0.8
```

**For Subtle Guidance:**
```
strength: 0.8
start_percent: 0.2
end_percent: 1.0
```

### KSampler Recommended Settings for Flux

```
steps: 30-40 (balance speed/quality)
cfg: 3.5-4.5 (Flux is very efficient with guidance)
sampler: "euler" or "dpmpp_2m"
scheduler: "karras" or "exponential"
denoise: 1.0 (full generation from scratch)
```

---

## FRAME-BY-FRAME PROCESSING LOOP

### Pseudo-code for Batch Processing

```python
# Load everything once
model = LoadCheckpoint("flux-1-dev")
controlnet = LoadControlNet("openpose")
vae = model.vae
clip = model.clip

# For each frame
for i, frame in enumerate(video_frames):
    # Extract pose
    pose_image = OpenPosePreprocessor(frame)
    
    # Generate prompt (static or dynamic)
    if use_qwen:
        prompt = QwenImageEncoder(frame).caption
        prompt = enhance_prompt(prompt, style)
    else:
        prompt = static_prompt
    
    # Encode text
    conditioning = CLIPTextEncode(prompt, clip)
    
    # Apply control
    controlled = ControlNetApply(
        conditioning,
        controlnet,
        pose_image,
        strength=1.0
    )
    
    # Generate image
    latent = KSampler(
        model=model,
        positive=controlled,
        steps=30,
        cfg=4.0
    )
    
    # Decode
    image = VAEDecode(latent, vae)
    
    # Post-process
    image = Upscale(image, "RealESRGAN_x4")
    image = ColorCorrect(image, original_frame)
    
    # Save frame
    output_frames.append(image)

# Reassemble with audio
final_video = VideoCombine(
    output_frames,
    original_audio,
    fps=24
)
```

---

## HARDWARE REQUIREMENTS

### Minimum Spec
- **GPU VRAM:** 12GB (RTX 3060, RTX 4060)
- **System RAM:** 16GB
- **Storage:** 50GB (for models)
- **Processing:** ~5-10 seconds per frame on RTX 4090

### Recommended Spec
- **GPU VRAM:** 24GB+ (RTX 4090, A100)
- **System RAM:** 32GB
- **Storage:** 100GB+ (for multiple models)
- **Processing:** ~2-3 seconds per frame

### Optimization Tips
1. Use `flux-1-dev-fp8.safetensors` (quantized) instead of full precision
2. Reduce step count to 20-25 for faster generation
3. Use smaller resolution (512x512) during testing
4. Implement frame batching if hardware allows

---

## DEPENDENCIES SUMMARY

### Python Packages
```
torch==2.0+
torchvision
transformers>=4.30
diffusers>=0.25
opencv-python
pillow
numpy
omegaconf
einops
huggingface-hub
qwen-vl-utils  # For Qwen encoder
```

### Models to Download
```
ComfyUI/models/
├── diffusion_models/
│   └── flux-1-dev.safetensors (or fp8 variant)
├── controlnet/
│   └── control_openpose-fp16.safetensors
├── upscale_models/
│   └── RealESRGAN_x4.pth
└── checkpoints/
    └── gfpgan/ (optional)
```

---

## COMMON ISSUES & SOLUTIONS

### Issue: "CUDA out of memory"
- Use fp8 quantized model: `flux-1-dev-fp8.safetensors`
- Reduce step count
- Use smaller resolution
- Enable memory optimization: `--memory-efficient-attention`

### Issue: "Pose not being followed"
- Increase ControlNet strength to 1.2-1.5
- Check that OpenPose preprocessor output shows clear skeleton
- Ensure poses are valid (not corrupted)

### Issue: "Generated image doesn't match original color"
- Use `ImageColorCorrection` node
- Sample original frame color values
- Increase prompt specificity about colors/lighting

### Issue: "Face looks distorted"
- Apply GFPGAN enhancement
- Increase prompt detail for facial features
- Reduce ControlNet strength slightly
- Use face-focused LoRA

### Issue: "Audio/video sync issues"
- Ensure frame rate is consistent (match input video)
- Use `VHS_AudioCombine` to properly attach audio
- Verify frame count matches audio duration
  ```
  frame_count = fps × audio_duration_seconds
  ```

---

## WORKFLOW FILES CHECKLIST

For production implementation, create:

```
comfyui_grok_workflow/
├── workflows/
│   ├── 01_test_single_frame.json
│   ├── 02_batch_frame_processing.json
│   ├── 03_full_video_with_audio.json
│   └── 04_with_color_correction.json
├── prompts/
│   ├── style_prompts.txt
│   └── character_templates.txt
├── scripts/
│   ├── frame_processor.py
│   ├── video_assembler.py
│   └── batch_worker.py
├── config/
│   ├── model_config.yaml
│   └── generation_settings.yaml
└── README.md
```

---

## NEXT STEPS

1. **Install All Extensions:**
   - VHS (Video Helper Suite)
   - ControlNet nodes
   - Qwen VL (optional)

2. **Download Models:**
   - Flux 1 Dev
   - OpenPose ControlNet
   - RealESRGAN upscaler
   - Optional: GFPGAN, LoRAs

3. **Create Test Workflow:**
   - Start with single frame generation
   - Test ControlNet strength
   - Fine-tune prompts

4. **Implement Batch Processing:**
   - Extract frames from test video
   - Generate transformed frames
   - Reassemble with audio

5. **Optimize & Scale:**
   - Profile performance
   - Implement multi-GPU if available
   - Batch by hardware capability

---

