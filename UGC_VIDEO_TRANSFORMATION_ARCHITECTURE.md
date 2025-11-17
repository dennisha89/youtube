# UGC Video Transformation Workflow Architecture
## ComfyUI Implementation Design

**Goal**: Transform UGC videos (change person, background, style) while preserving original movements

**Version**: 1.0
**Date**: 2025-11-17

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Node Flow](#complete-node-flow)
3. [Data Types & Connections](#data-types--connections)
4. [Batch Processing Strategy](#batch-processing-strategy)
5. [Prompt Strategy](#prompt-strategy)
6. [ControlNet Configuration](#controlnet-configuration)
7. [Performance Optimization](#performance-optimization)
8. [Alternative Approaches](#alternative-approaches)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

### Workflow Pipeline

```
Input Video → Frame Extraction → Pose Analysis → Prompt Generation → 
Image Generation (Flux + ControlNet) → Refinement Pass 1 → 
Refinement Pass 2 → Post-Processing → Audio Sync → Final Video
```

### Required Extensions

1. **Video Helper Suite (VHS)** - Video I/O operations
2. **ComfyUI-Advanced-ControlNet** - Pose preservation
3. **Flux.1 Dev Model** - Image generation
4. **InstantX ControlNet Union Pro** - OpenPose support
5. **ComfyUI-VideoHelperSuite** - Frame/video conversion
6. **ComfyUI-Frame-Interpolation** (Optional) - Smoothing
7. **Ultimate SD Upscale** (Optional) - Enhancement

---

## Complete Node Flow

### Phase 1: Video Input & Frame Extraction

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: VIDEO INPUT & DECOMPOSITION                       │
└─────────────────────────────────────────────────────────────┘

[UGC Video Downloader]
         ↓ (STRING: video_path)
[VHS Load Video]
    ├──→ (IMAGE: frames_batch)     # All frames as batch
    ├──→ (INT: frame_count)        # Total frames
    ├──→ (AUDIO: audio_track)      # Original audio
    └──→ (FLOAT: fps)              # Frame rate info
```

**Nodes Required**:
- `UGCVideoDownloader` (existing node)
- `VHS Load Video` node from Video Helper Suite

**Parameters**:
- `force_rate`: 0 (keep original FPS)
- `frame_load_cap`: 0 (load all frames)
- `skip_first_frames`: 0
- `select_every_nth`: 1 (process every frame)

**Data Types**:
- OUTPUT: `IMAGE` tensor [N, H, W, C] where N = number of frames

---

### Phase 2: Frame Analysis & Prompt Generation

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: FRAME ANALYSIS                                    │
└─────────────────────────────────────────────────────────────┘

[Frames Batch] 
    ├──→ [Sample Frame Selector]
    │         ↓ (IMAGE: key_frames)
    │    [Qwen2-VL Image Encoder]*
    │         ↓ (STRING: scene_description)
    │    [GPT-4 Vision / Claude Vision]*
    │         ↓ (STRING: detailed_prompt)
    │
    └──→ [ControlNet OpenPose Preprocessor]
              ↓ (IMAGE: pose_maps_batch)
```

**Nodes Required**:
- `Sample Frame Selector` - Custom node to select keyframes (every Nth frame)
- `Qwen2-VL` or `CLIP Interrogator` - For prompt generation
- `DWPreprocessor` - For OpenPose detection

**Parameters**:
- Sample every 10-30 frames for prompt analysis
- OpenPose: `detect_hand: enabled`, `detect_body: enabled`, `detect_face: enabled`

**Data Types**:
- Pose maps: `IMAGE` tensor [N, H, W, C] - grayscale pose visualization
- Prompts: `STRING` - text description of scene

---

### Phase 3: Prompt Consistency System

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: PROMPT GENERATION & CONSISTENCY                   │
└─────────────────────────────────────────────────────────────┘

[Scene Description]
         ↓
[User Transformation Prompt]
         ↓
[Prompt Template Builder]
         ↓
[Batch Prompt Replicator]
         ↓ (STRING_BATCH: prompts_per_frame)
```

**Prompt Template Structure**:
```
Base Prompt: "A [NEW_SUBJECT] in [NEW_STYLE], [NEW_BACKGROUND]"
Consistency Keywords: "[SUBJECT_DETAIL], [CLOTHING], [LIGHTING]"
Quality Tags: "high quality, detailed, 8k, professional photography"
Negative: "blurry, distorted, deformed, inconsistent, flickering"
```

**Example Transformation**:
```
Original: Man reviewing protein powder in gym
New: "Woman with blonde hair in cyberpunk style, neon city background, 
      wearing futuristic athletic wear, purple and blue lighting, 
      high quality, detailed, 8k, professional photography"
```

**Nodes Required**:
- `Text Input` node (built-in)
- `String to List` node - Replicate prompt for each frame
- `Prompt Scheduler` (optional) - For gradual transitions

---

### Phase 4: Image Generation with Flux + ControlNet

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: FLUX GENERATION (Main Pass)                       │
└─────────────────────────────────────────────────────────────┘

[Load Flux.1 Dev Checkpoint]
         ↓ (MODEL)
         
[Dual CLIP Text Encode (Prompt Encode)]
    ├──→ Positive: (CONDITIONING)
    └──→ Negative: (CONDITIONING)

[Apply ControlNet (InstantX Union Pro)]
    ├── Model Input: (MODEL)
    ├── Conditioning: (CONDITIONING)
    ├── Pose Maps: (IMAGE: pose_maps_batch)
    ├── Strength: 0.8-1.0
    └──→ (CONDITIONING_MODIFIED)

[Empty Latent Image Batch]
    ├── Width: 1024
    ├── Height: 1024
    ├── Batch Size: [frame_count]
    └──→ (LATENT)

[KSampler Advanced]
    ├── Model: (MODEL)
    ├── Positive: (CONDITIONING_MODIFIED)
    ├── Negative: (CONDITIONING)
    ├── Latent: (LATENT)
    ├── Steps: 20-30
    ├── CFG: 7.0-8.0
    ├── Sampler: "euler" or "dpmpp_2m"
    ├── Scheduler: "normal"
    ├── Seed: [random or fixed]
    └──→ (LATENT: generated_latents)

[VAE Decode]
    └──→ (IMAGE: generated_frames)
```

**Critical Parameters**:

**ControlNet Settings**:
- `strength`: 0.85 (preserve 85% of pose structure)
- `start_percent`: 0.0 (apply from beginning)
- `end_percent`: 1.0 (apply throughout)

**Sampler Settings**:
- `steps`: 25 (balance quality/speed)
- `cfg_scale`: 7.5 (balance prompt adherence/creativity)
- `denoise`: 1.0 (full generation, not img2img)

**Model Loading**:
- Use FP8 quantized model for memory savings: `flux1-dev-fp8.safetensors`
- Alternative: GGUF Q4 or Q5 for extreme memory constraints

---

### Phase 5: First Refinement Pass

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: REFINEMENT PASS 1 - Temporal Consistency          │
└─────────────────────────────────────────────────────────────┘

[Generated Frames]
         ↓
[Frame Difference Analyzer]*
    ├── Compare frame N with N+1
    ├── Detect flickering
    └──→ (MASK: inconsistent_regions)

[KSampler (img2img mode)]
    ├── Input Images: (IMAGE: generated_frames)
    ├── ControlNet Pose: (IMAGE: pose_maps_batch)
    ├── Denoise: 0.3-0.4 (subtle refinement)
    ├── Steps: 15
    └──→ (IMAGE: refined_frames_v1)
```

**Purpose**: Reduce frame-to-frame flickering and inconsistencies

**Parameters**:
- Low denoise (0.3-0.4) to preserve main generation
- Reapply same prompt + ControlNet for consistency
- Optional: Use AnimateDiff for motion smoothing

---

### Phase 6: Second Refinement Pass

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: REFINEMENT PASS 2 - Detail Enhancement            │
└─────────────────────────────────────────────────────────────┘

[Refined Frames V1]
         ↓
[Detail Enhancer] (Optional)
    ├── Method: Ultimate SD Upscale
    ├── Upscale Factor: 1.5x or 2x
    ├── Tile Size: 512
    ├── Denoise: 0.2-0.3
    └──→ (IMAGE: refined_frames_v2)

OR

[Face Restoration]* (if subject is person)
    ├── CodeFormer / GFPGAN
    └──→ (IMAGE: face_enhanced_frames)
```

**Purpose**: Polish details, upscale if needed

**Options**:
1. **Upscaling**: Use for higher resolution output
2. **Face Fix**: Use if faces are blurry/distorted
3. **Skip**: If quality is already good

---

### Phase 7: Post-Processing

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 7: POST-PROCESSING                                   │
└─────────────────────────────────────────────────────────────┘

[Refined Frames]
         ↓
[Color Correction]
    ├── Adjust brightness
    ├── Saturation
    ├── Contrast
    └──→ (IMAGE: color_corrected)

[Frame Interpolation]* (Optional)
    ├── RIFE or FILM
    ├── Multiply FPS by 2x or 4x
    └──→ (IMAGE: interpolated_frames)

[Image Sharpen / Denoise]*
    └──→ (IMAGE: final_frames)
```

**Purpose**: Final polish and frame smoothing

**Parameters**:
- Color correction: Subtle adjustments (±10%)
- Interpolation: Only if original FPS < 24
- Sharpen: Strength 0.3-0.5

---

### Phase 8: Audio Sync & Final Video

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 8: AUDIO SYNC & VIDEO COMPILATION                    │
└─────────────────────────────────────────────────────────────┘

[Final Frames] + [Original Audio] + [FPS]
         ↓
[VHS Combine Video]
    ├── Frames: (IMAGE: final_frames)
    ├── Audio: (AUDIO: audio_track)
    ├── FPS: (FLOAT: fps)
    ├── Format: "video/h264-mp4"
    ├── Quality: 9 (high)
    └──→ (VIDEO: final_video)

[VHS Save Video]
    └──→ Output: output/transformed_video.mp4
```

**Final Export Settings**:
- Codec: H.264
- Audio Codec: AAC
- Bitrate: 8-12 Mbps
- Audio Sample Rate: 48kHz

---

## Data Types & Connections

### ComfyUI Core Data Types

| Data Type | Description | Shape | Usage |
|-----------|-------------|-------|-------|
| `IMAGE` | RGB image tensor | `[B, H, W, C]` | Frames, pose maps, generated images |
| `LATENT` | Latent space representation | `[B, 4, H/8, W/8]` | For diffusion model processing |
| `CONDITIONING` | Text embedding + metadata | `[(tensor, dict)]` | Positive/negative prompts |
| `MODEL` | Loaded diffusion model | Object | Flux.1 Dev checkpoint |
| `VAE` | Encoder/decoder | Object | For latent ↔ image conversion |
| `CLIP` | Text encoder | Object | For prompt encoding |
| `CONTROL_NET` | ControlNet model | Object | For pose conditioning |
| `STRING` | Text data | String | Prompts, paths, metadata |
| `INT` | Integer | Int | Frame count, batch size |
| `FLOAT` | Float | Float | FPS, strength values |
| `AUDIO` | Audio waveform | Tensor | Audio track |

### Data Flow Example

```
Video File (STRING)
    ↓
VHS Load Video
    ├→ IMAGE [120, 1024, 1024, 3]  # 120 frames
    ├→ AUDIO [2, 48000*duration]    # Stereo audio
    └→ FLOAT 30.0                   # 30 FPS
           ↓
OpenPose Preprocessor
    ↓ IMAGE [120, 1024, 1024, 3]    # Pose maps (grayscale)
           ↓
Apply ControlNet → CONDITIONING
    ↓
KSampler → LATENT [120, 4, 128, 128]
    ↓
VAE Decode → IMAGE [120, 1024, 1024, 3]
    ↓
VHS Combine Video → VIDEO
```

---

## Batch Processing Strategy

### Challenge: Memory Management

Processing 120+ frames simultaneously can exceed VRAM limits. Solutions:

### Strategy 1: Chunk Processing (Recommended)

```
┌────────────────────────────────────────────────┐
│ CHUNK-BASED PROCESSING                        │
└────────────────────────────────────────────────┘

Full Video (300 frames)
    ↓
[Video Chunk Splitter]*
    ├→ Chunk 1: Frames 0-29 (30 frames)
    ├→ Chunk 2: Frames 30-59 (30 frames)
    ├→ Chunk 3: Frames 60-89 (30 frames)
    └→ ... (10 chunks total)

Each chunk:
    → Process through full pipeline
    → Save intermediate results
    
[Video Chunk Merger]*
    → Combine all chunks
    → Ensure smooth transitions
```

**Implementation**:
```python
# Custom node pseudocode
chunk_size = 30  # Frames per batch
overlap = 2      # Overlap frames for smooth transition

for i in range(0, total_frames, chunk_size - overlap):
    chunk = frames[i:i+chunk_size]
    processed_chunk = process_pipeline(chunk)
    save_chunk(processed_chunk, i)

# Blend overlapping frames
final_video = blend_chunks(all_chunks, overlap)
```

**Chunk Size Recommendations**:
- 24GB VRAM: 30-50 frames
- 16GB VRAM: 20-30 frames
- 12GB VRAM: 10-20 frames
- 8GB VRAM: 5-10 frames

### Strategy 2: Sequential Processing with Frame Buffer

```
┌────────────────────────────────────────────────┐
│ SEQUENTIAL FRAME PROCESSING                   │
└────────────────────────────────────────────────┘

[Frame Iterator]
    ↓
For each frame:
    [Load Frame N]
    [Load Pose N]
    [Generate with ControlNet]
    [Save to Buffer]
    
[Buffer Combiner]
    → Merge all processed frames
```

**Pros**: Minimal VRAM usage
**Cons**: Slower, harder to maintain consistency

### Strategy 3: Hybrid Approach (Best)

```
1. Process keyframes first (every 30th frame) at high quality
2. Process intermediate frames with lower denoise, using keyframes as reference
3. Blend results for temporal consistency
```

**Benefits**:
- Memory efficient
- Maintains visual consistency
- Faster than full sequential

---

## Prompt Strategy

### Challenge: Maintaining Consistency Across Frames

The same prompt must generate consistent characters/scenes across all frames.

### Solution 1: Static Global Prompt + ControlNet

```
Global Prompt (applied to ALL frames):
"A woman with long blonde hair wearing a black leather jacket, 
cyberpunk style, neon purple lighting, futuristic city background, 
detailed face, 8k, professional photography"

+ ControlNet Pose (different per frame)
```

**Advantages**:
- Maximum consistency
- Simplest implementation
- Works well with strong ControlNet

**Disadvantages**:
- No dynamic scene changes
- Can feel static

### Solution 2: Keyframe-Based Prompt Interpolation

```
Frame 0: "woman in cyberpunk city, night scene, purple lighting"
Frame 60: "woman in cyberpunk city, night scene, blue lighting"
Frame 120: "woman in cyberpunk city, dawn scene, orange lighting"

Intermediate frames: Interpolate between keyframes
```

**Implementation**:
Use `Prompt Scheduler` or `Prompt Travel` nodes for gradual transitions.

### Solution 3: Character LoRA (Recommended for Best Results)

```
Step 1: Generate 10-15 reference images from first pass
Step 2: Train character LoRA on reference images (30-100 steps)
Step 3: Re-run pipeline with LoRA enabled

Prompt: "SUBJECT_LORA, in cyberpunk city, ..."
```

**Benefits**:
- Extremely consistent character
- Maintains identity across all frames
- Allows dynamic scene changes

**Tools**:
- Kohya-ss for LoRA training
- ComfyUI LoRA loader nodes

### Solution 4: IP-Adapter for Face Consistency

```
[Reference Image] (best frame from first pass)
         ↓
[IP-Adapter Model]
         ↓
[Apply to All Frames]
```

**Use Case**: When you need the same face across all frames

**Nodes**: ComfyUI-IPAdapter-plus

---

## ControlNet Configuration

### OpenPose ControlNet Settings

```
┌────────────────────────────────────────────────┐
│ CONTROLNET STRENGTH CONFIGURATION              │
└────────────────────────────────────────────────┘

Strength Range: 0.0 to 1.0

0.3 - 0.5: Loose pose guidance
    → Allows significant creative freedom
    → Use for: Stylized interpretations
    
0.5 - 0.7: Moderate pose guidance
    → Balanced between pose and prompt
    → Use for: General transformations
    
0.7 - 0.9: Strong pose guidance (RECOMMENDED)
    → Closely follows original pose
    → Use for: Movement preservation
    
0.9 - 1.0: Very strict pose guidance
    → Almost exact pose replication
    → Use for: Dance videos, precise movements
```

### Recommended Settings by Use Case

**Product Review Video**:
```yaml
strength: 0.75
start_percent: 0.0
end_percent: 1.0
preprocessor: "DWPose"
detect_hand: true
detect_body: true
detect_face: true
```

**Dance/Performance Video**:
```yaml
strength: 0.9
start_percent: 0.0
end_percent: 1.0
preprocessor: "OpenPose"
detect_hand: true
detect_body: true
detect_face: true
```

**Talking Head Video**:
```yaml
strength: 0.8
start_percent: 0.0
end_percent: 1.0
preprocessor: "DWPose" (more accurate)
detect_hand: false
detect_body: false
detect_face: true
```

### Multi-ControlNet Strategy

For maximum control, combine multiple ControlNets:

```
[Apply ControlNet Stack]
    ├── OpenPose: 0.8 (pose)
    ├── Depth: 0.4 (spatial structure)
    └── Canny: 0.3 (edge details)
```

**When to use**:
- Complex scenes with backgrounds
- Need to preserve spatial relationships
- High-quality production

**ControlNet Union Pro** supports this natively.

---

## Performance Optimization

### Memory Optimization

#### 1. Model Quantization

```
┌────────────────────────────────────────────────┐
│ MODEL SIZE COMPARISON                          │
└────────────────────────────────────────────────┘

Flux.1 Dev Full (BF16): ~24GB
Flux.1 Dev FP8: ~12GB (RECOMMENDED)
Flux.1 Dev GGUF Q8: ~8GB
Flux.1 Dev GGUF Q5: ~6GB
Flux.1 Dev GGUF Q4: ~4GB
```

**Recommendation**: Use FP8 for quality/performance balance

#### 2. VAE Optimization

```yaml
Use tiled VAE for large images:
  tile_size: 512
  overlap: 64
  
This reduces VRAM usage by 50-70%
```

**Node**: `VAE Encode/Decode (Tiled)`

#### 3. Attention Optimization

Enable in ComfyUI settings:
- `--use-split-cross-attention` (saves VRAM)
- `--use-quad-cross-attention` (even more savings)
- `--lowvram` (for <12GB cards)

#### 4. Batch Size Tuning

```python
# Find optimal batch size
batch_sizes = [5, 10, 15, 20, 30]

for batch_size in batch_sizes:
    try:
        process_batch(frames[:batch_size])
        print(f"✓ {batch_size} frames works")
    except OutOfMemoryError:
        optimal_batch = batch_size - 5
        break
```

### Speed Optimization

#### 1. Sampler Selection

```
┌────────────────────────────────────────────────┐
│ SAMPLER SPEED COMPARISON (25 steps)           │
└────────────────────────────────────────────────┘

Euler: 100% (baseline, fastest)
Euler A: 105%
DPM++ 2M: 120%
DPM++ 2M Karras: 125%
DPM++ SDE: 140%
DDIM: 110%

Quality ranking (high to low):
1. DPM++ 2M Karras ⭐ (RECOMMENDED)
2. DPM++ 2M
3. Euler A
4. Euler
5. DDIM
```

**Recommendation**: DPM++ 2M Karras, 20-25 steps

#### 2. Step Count Optimization

```
Quality vs Speed:
- 15 steps: Fast, acceptable for previews
- 20 steps: Good balance, production quality
- 25 steps: High quality, minimal improvement beyond this
- 30+ steps: Diminishing returns
```

#### 3. Resolution Strategy

```
Option A: Generate at native resolution (1024x1024)
  → Slower but highest quality

Option B: Generate at 768x768, upscale to 1024x1024
  → 40% faster, slight quality loss
  → Use Ultimate SD Upscale for final pass

Option C: Generate at 512x512, upscale to 1024x1024
  → 70% faster, noticeable quality loss
  → Good for testing/previews
```

#### 4. Frame Skipping (Experimental)

```
Process every 2nd frame → Interpolate missing frames
  → 50% reduction in processing time
  → Use RIFE for frame interpolation
  → Quality depends on motion speed
```

**When to use**:
- Static scenes
- Slow movements
- Limited compute budget

---

## Alternative Approaches

### Alternative 1: AnimateDiff Instead of Frame-by-Frame

```
┌────────────────────────────────────────────────┐
│ ANIMATEDIFF APPROACH                           │
└────────────────────────────────────────────────┘

[First Frame] + [Pose Sequence]
         ↓
[AnimateDiff Model]
    ├── Motion Module
    ├── ControlNet OpenPose
    └──→ Generate full video sequence

Advantages:
✓ Better temporal consistency
✓ Smoother motion
✓ Faster processing

Disadvantages:
✗ Less control over individual frames
✗ May drift from original motion
✗ Requires AnimateDiff-compatible checkpoint
```

**When to use**:
- Short clips (2-5 seconds)
- Simpler transformations
- Temporal consistency is critical

### Alternative 2: Ebsynth-Based Approach

```
┌────────────────────────────────────────────────┐
│ EBSYNTH PROPAGATION APPROACH                   │
└────────────────────────────────────────────────┘

Step 1: Generate 3-5 keyframes with Flux + ControlNet
Step 2: Use Ebsynth to propagate style to all frames
Step 3: Blend results

Advantages:
✓ Extremely fast (only generate keyframes)
✓ Perfect temporal consistency
✓ Low VRAM usage

Disadvantages:
✗ Requires external tool (Ebsynth)
✗ Quality depends on keyframe spacing
✗ May create artifacts on fast motion
```

**Tools**: Ebsynth Utility, ComfyUI-Ebsynth nodes

### Alternative 3: Video2Video with Temporal Attention

```
┌────────────────────────────────────────────────┐
│ TEMPORAL-AWARE VIDEO2VIDEO                    │
└────────────────────────────────────────────────┘

[Input Video]
         ↓
[Flux Video2Video] (hypothetical future model)
    ├── Temporal Self-Attention
    ├── Cross-Frame Consistency
    └──→ Output Video

Status: Not yet available for Flux
Alternative: Use SD 1.5 + Temporal ControlNet
```

**Future Option**: When Flux video models become available

### Alternative 4: If ControlNet Not Available

```
┌────────────────────────────────────────────────┐
│ FALLBACK WITHOUT CONTROLNET                   │
└────────────────────────────────────────────────┘

Option A: Image-to-Image with Low Denoise
[Original Frame] → [Flux img2img] (denoise 0.4-0.6)
    → Preserves structure through latent space

Option B: Depth + Canny Conditioning
[Original Frame] → [Depth Map] + [Canny Edges]
    → Use as conditioning instead of pose

Option C: GLIGEN Bounding Boxes
[Original Frame] → [Detect person bbox] → [GLIGEN]
    → Position-based conditioning
```

### Alternative 5: Minimal Resource Workflow

```
┌────────────────────────────────────────────────┐
│ LOW-END HARDWARE WORKFLOW                      │
└────────────────────────────────────────────────┘

For 8GB VRAM or less:

1. Use Flux NF4 (3.5GB) or Q4 GGUF (4GB)
2. Process 1 frame at a time
3. Use 512x512 resolution
4. 15 steps with Euler sampler
5. Upscale final result with RealESRGAN
6. Interpolate frames with RIFE

Total Processing Time (60sec video):
  ~2-4 hours on RTX 3060 8GB
```

---

## Implementation Roadmap

### Phase 1: Basic Workflow (Week 1)

**Goal**: Single-pass video transformation

1. ✅ Video loading and frame extraction
2. ✅ OpenPose preprocessing
3. ✅ Basic Flux generation with ControlNet
4. ✅ Video reassembly with audio
5. ⬜ Test with 5-10 second clips

**Expected Output**: Working but inconsistent transformations

### Phase 2: Consistency Improvements (Week 2)

**Goal**: Temporal consistency

1. ⬜ Implement chunk-based processing
2. ⬜ Add prompt consistency mechanisms
3. ⬜ Add first refinement pass
4. ⬜ Test character consistency across frames

**Expected Output**: Smoother, more consistent videos

### Phase 3: Quality Enhancements (Week 3)

**Goal**: Production-quality output

1. ⬜ Implement second refinement pass
2. ⬜ Add upscaling options
3. ⬜ Add post-processing (color correction, sharpening)
4. ⬜ Optimize parameters for different use cases

**Expected Output**: High-quality transformations

### Phase 4: Advanced Features (Week 4+)

**Goal**: Professional features

1. ⬜ Character LoRA training integration
2. ⬜ IP-Adapter for face consistency
3. ⬜ Multi-ControlNet support
4. ⬜ Batch video processing
5. ⬜ Preset templates for common transformations

**Expected Output**: Production-ready system

### Phase 5: Optimization (Ongoing)

**Goal**: Speed and efficiency

1. ⬜ Memory profiling and optimization
2. ⬜ Parameter tuning for quality/speed balance
3. ⬜ Alternative workflow testing
4. ⬜ Documentation and examples

---

## Node-by-Node Parameter Reference

### VHS Load Video
```yaml
inputs:
  video: upload
  force_rate: 0
  force_size: "Disabled"
  custom_width: 512
  custom_height: 512
  frame_load_cap: 0
  skip_first_frames: 0
  select_every_nth: 1

outputs:
  IMAGE: frames
  frame_count: int
  audio: audio
  video_info: dict
```

### DWPreprocessor (OpenPose)
```yaml
inputs:
  image: IMAGE
  detect_hand: "enable"
  detect_body: "enable"
  detect_face: "enable"
  resolution: 1024
  bbox_detector: "yolox_l.onnx"
  pose_estimator: "dw-ll_ucoco_384.onnx"

outputs:
  IMAGE: pose_maps
```

### Load Flux Checkpoint
```yaml
inputs:
  ckpt_name: "flux1-dev-fp8.safetensors"
  
outputs:
  MODEL: model
  CLIP: clip
  VAE: vae
```

### CLIPTextEncode
```yaml
inputs:
  clip: CLIP
  text: STRING

outputs:
  CONDITIONING: conditioning
```

### Apply ControlNet
```yaml
inputs:
  conditioning: CONDITIONING
  control_net: CONTROL_NET
  image: IMAGE (pose maps)
  strength: 0.85
  start_percent: 0.0
  end_percent: 1.0

outputs:
  CONDITIONING: modified_conditioning
```

### Empty Latent Image
```yaml
inputs:
  width: 1024
  height: 1024
  batch_size: 30

outputs:
  LATENT: latent
```

### KSampler Advanced
```yaml
inputs:
  model: MODEL
  add_noise: "enable"
  noise_seed: [random]
  steps: 25
  cfg: 7.5
  sampler_name: "dpmpp_2m"
  scheduler: "karras"
  positive: CONDITIONING
  negative: CONDITIONING
  latent_image: LATENT
  start_at_step: 0
  end_at_step: 25
  return_with_leftover_noise: "disable"

outputs:
  LATENT: latent_output
```

### VAE Decode
```yaml
inputs:
  samples: LATENT
  vae: VAE
  tile_size: 512  # If using tiled VAE

outputs:
  IMAGE: decoded_images
```

### VHS Combine Video
```yaml
inputs:
  images: IMAGE
  frame_rate: 30
  loop_count: 0
  filename_prefix: "transformed_"
  format: "video/h264-mp4"
  pix_fmt: "yuv420p"
  crf: 18  # Lower = higher quality
  save_metadata: true
  audio: AUDIO (optional)

outputs:
  Filenames: list
  VIDEO: video
```

---

## Example Complete Workflow JSON Structure

```json
{
  "nodes": {
    "1": {
      "type": "UGCVideoDownloader",
      "inputs": {"url": "https://youtube.com/..."},
      "outputs": ["video_path"]
    },
    "2": {
      "type": "VHSLoadVideo",
      "inputs": {"video": "1:video_path"},
      "outputs": ["frames", "audio", "fps"]
    },
    "3": {
      "type": "DWPreprocessor",
      "inputs": {
        "image": "2:frames",
        "detect_hand": "enable",
        "detect_body": "enable",
        "detect_face": "enable"
      },
      "outputs": ["pose_maps"]
    },
    "4": {
      "type": "LoadCheckpoint",
      "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"},
      "outputs": ["model", "clip", "vae"]
    },
    "5": {
      "type": "CLIPTextEncode",
      "inputs": {
        "clip": "4:clip",
        "text": "woman in cyberpunk city..."
      },
      "outputs": ["positive_conditioning"]
    },
    "6": {
      "type": "ApplyControlNet",
      "inputs": {
        "conditioning": "5:positive_conditioning",
        "control_net": "controlnet_union_pro",
        "image": "3:pose_maps",
        "strength": 0.85
      },
      "outputs": ["modified_conditioning"]
    },
    "7": {
      "type": "EmptyLatentImage",
      "inputs": {
        "width": 1024,
        "height": 1024,
        "batch_size": 30
      },
      "outputs": ["latent"]
    },
    "8": {
      "type": "KSamplerAdvanced",
      "inputs": {
        "model": "4:model",
        "positive": "6:modified_conditioning",
        "latent_image": "7:latent",
        "steps": 25,
        "cfg": 7.5
      },
      "outputs": ["generated_latents"]
    },
    "9": {
      "type": "VAEDecode",
      "inputs": {
        "samples": "8:generated_latents",
        "vae": "4:vae"
      },
      "outputs": ["generated_frames"]
    },
    "10": {
      "type": "VHSCombineVideo",
      "inputs": {
        "images": "9:generated_frames",
        "audio": "2:audio",
        "frame_rate": "2:fps"
      },
      "outputs": ["final_video"]
    }
  }
}
```

---

## Troubleshooting Guide

### Issue: Flickering Between Frames

**Causes**:
- Different random seeds per frame
- Weak ControlNet strength
- Inconsistent prompts

**Solutions**:
1. Use fixed seed for all frames
2. Increase ControlNet strength to 0.9
3. Add character LoRA or IP-Adapter
4. Use AnimateDiff for temporal smoothing

### Issue: Out of Memory

**Solutions**:
1. Reduce batch size (process fewer frames at once)
2. Use FP8 or GGUF quantized model
3. Enable tiled VAE
4. Reduce resolution to 768x768 or 512x512
5. Use `--lowvram` flag in ComfyUI

### Issue: Pose Not Preserved

**Solutions**:
1. Increase ControlNet strength to 0.9-1.0
2. Check OpenPose preprocessing quality
3. Use DWPose instead of OpenPose (more accurate)
4. Ensure pose maps are being applied correctly

### Issue: Character Inconsistency

**Solutions**:
1. Train character LoRA on reference frames
2. Use IP-Adapter with reference image
3. Add more specific character details to prompt
4. Use higher CFG scale (8-9)

### Issue: Slow Processing

**Solutions**:
1. Use FP8 model instead of full precision
2. Reduce step count to 20
3. Use Euler sampler instead of DPM++
4. Process fewer frames per batch
5. Consider frame skipping + interpolation

---

## Cost Estimation

### Hardware Requirements

**Minimum** (Testing):
- GPU: RTX 3060 12GB
- RAM: 16GB
- Storage: 100GB

**Recommended** (Production):
- GPU: RTX 4090 24GB or A6000 48GB
- RAM: 32GB
- Storage: 500GB SSD

**Cloud Options**:
- RunPod RTX 4090: ~$0.60/hour
- Vast.ai RTX 4090: ~$0.40-0.80/hour
- Modal Labs: ~$1.50/hour (A100)

### Processing Time Estimates

**60-second video (1800 frames at 30fps)**:

| Hardware | Resolution | Quality | Time |
|----------|-----------|---------|------|
| RTX 4090 | 1024x1024 | High | 4-6 hours |
| RTX 4090 | 768x768 | Medium | 2-3 hours |
| RTX 3090 | 1024x1024 | High | 6-8 hours |
| RTX 3060 | 512x512 | Low | 8-12 hours |

**Optimization**: Process keyframes only (10x speedup)

### Cost Per Video

Cloud processing (RTX 4090):
- 60s video: $2.40-3.60
- 30s video: $1.20-1.80
- 15s video: $0.60-0.90

---

## Best Practices

### 1. Start Small
- Test with 5-10 second clips first
- Iterate on single frames before full video
- Use preview mode (lower resolution/steps)

### 2. Optimize Prompts First
- Generate test frames with different prompts
- Find the most consistent prompt template
- Document what works for different content types

### 3. Incremental Quality
- First pass: Quick generation with lower settings
- Review results
- Second pass: Higher quality on successful attempts

### 4. Save Checkpoints
- Save intermediate results
- Don't process everything in one go
- Allows resuming if something fails

### 5. Version Control
- Save workflow JSONs with version numbers
- Document parameter changes
- Keep notes on what works

---

## Conclusion

This architecture provides a comprehensive blueprint for transforming UGC videos while preserving motion. The modular design allows for:

- **Flexibility**: Swap nodes based on available resources
- **Scalability**: Process from single frames to full videos
- **Quality**: Multiple refinement passes for production-grade output
- **Efficiency**: Batch processing and optimization strategies

**Next Steps**:
1. Set up ComfyUI with required extensions
2. Test basic workflow with short clip
3. Iterate on quality and consistency
4. Scale to longer videos
5. Develop presets for common use cases

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Author**: Claude (Anthropic)
**Status**: Architecture Design Complete

