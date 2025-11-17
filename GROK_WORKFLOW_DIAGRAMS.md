# Grok Workflow: Visual Diagrams & Flowcharts

## Complete Grok Workflow Architecture

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                   GROK WORKFLOW - COMPLETE ARCHITECTURE                        ║
╚════════════════════════════════════════════════════════════════════════════════╝

STEP 1: INPUT VIDEO
═══════════════════
┌──────────────────────┐
│   Input MP4 Video    │
│   (24/30/60 FPS)     │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  VHS_LoadVideo       │  Load full video sequence
│                      │
│ • force_rate: auto   │
│ • frame_load_cap: 0  │
└──────────┬───────────┘
           │
           ↓
        [VIDEO] object with frame sequence


STEP 2: FRAME EXTRACTION & AUDIO SPLIT
═══════════════════════════════════════
[VIDEO] ─────────┬────────────────────────────────┐
                 │                                │
                 ↓                                ↓
         ┌───────────────────┐          ┌──────────────────┐
         │  VHS_SplitVideo   │          │  LoadAudio       │
         │                   │          │                  │
         │ force_size: keep  │          │ or               │
         │ custom_width: 512 │          │ VHS_LoadAudio    │
         └─────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   ↓                             ↓
           [IMAGE] Sequence          [AUDIO] object
           (frame 1, 2, 3...)        (sample_rate)


STEP 3: POSE EXTRACTION (Per-Frame Process)
═════════════════════════════════════════════
For each [IMAGE] frame:

    [Original Frame IMAGE]
           │
           ↓
    ┌─────────────────────────────┐
    │  OpenPose Preprocessor      │  Extract skeleton joints
    │                             │
    │  • include_body: true       │
    │  • include_hand: false      │
    │  • include_face: false      │
    └─────────┬───────────────────┘
              │
              ↓
    [Pose Skeleton IMAGE]
    (17 keypoints: head, shoulders,
     elbows, wrists, hips, knees, ankles)
              │
              ├────→ Save for debugging
              │
              └────→ Feed to ControlNet


STEP 4: TEXT PROMPT PREPARATION
═════════════════════════════════
Option A: STATIC PROMPT (Simple)
┌────────────────────────────────────────┐
│ PrimitiveNode (STRING)                 │
│                                        │
│ "Professional woman in navy blazer,    │
│  modern office, studio lighting, 8K"   │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────┐
│  CLIPTextEncode      │  Encode text to embeddings
│                      │
│ text: [prompt]       │
│ clip: [from model]   │
└────────┬─────────────┘
         │
         ↓
  [CONDITIONING] embedding


Option B: DYNAMIC PROMPT (with Qwen - for each frame)
┌──────────────────────┐
│  Original Frame      │
│  [IMAGE]             │
└────────┬─────────────┘
         │
         ↓
┌──────────────────────────────┐
│  QwenImageEncoder            │  Analyze image and generate caption
│                              │
│  image: [original frame]     │
│  model: "qwen-vl-max"        │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│  Generated Caption           │
│  (contextual description)    │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│  String Concatenation        │  Combine caption + style
│  caption + ", professional   │
│   photography, 8K"           │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────┐
│  CLIPTextEncode      │
└────────┬─────────────┘
         │
         ↓
  [CONDITIONING] embedding


STEP 5: MODEL INITIALIZATION (Load Once)
══════════════════════════════════════════
┌────────────────────────────────┐
│  CheckpointLoader              │
│                                │
│  ckpt_name:                    │
│  "flux-1-dev-fp8.safetensors"  │ ← Memory efficient version
│                                │
└─┬──────────────┬──────────────┬┘
  │              │              │
  ↓              ↓              ↓
[MODEL]      [CLIP]          [VAE]
(U-Net)      (text          (encoder
 Flux      encoder)        decoder)


┌────────────────────────────────┐
│  ControlNetLoader              │
│                                │
│  control_net_name:             │
│  "control_openpose-fp16"       │ ← OpenPose model
│                                │
└──────────────┬─────────────────┘
               │
               ↓
         [CONTROL_NET]


Optional - LoRA for Style:
┌────────────────────────────────┐
│  LoraLoader                    │
│                                │
│  lora_name: "professional_photo" │
│  strength_model: 1.0           │
│  strength_clip: 1.0            │
│                                │
└─┬──────────────┬───────────────┘
  │              │
  ↓              ↓
[MODEL]      [CLIP]  ← Modified with style


STEP 6: CONTROLNET APPLICATION
════════════════════════════════
Combines conditioning with pose guidance:

           [CONDITIONING]  (from CLIPTextEncode)
                 │
                 │
           [CONTROL_NET]  (from ControlNetLoader)
                 │
          ┌──────┴──────┐
          │             │
    [Pose IMAGE]   [CONDITIONING]
    (skeleton)     (original)
          │             │
          └──────┬──────┘
                 ↓
        ┌────────────────────────────┐
        │  ControlNetApply           │  Merge pose with text guidance
        │                            │
        │  • strength: 1.0           │
        │  • start_percent: 0.0      │
        │  • end_percent: 0.8        │
        │                            │
        └────────┬───────────────────┘
                 │
                 ↓
    [Modified CONDITIONING]
    (text guidance + pose control)


STEP 7: IMAGE GENERATION
═════════════════════════
┌─────────────────────────────────┐
│  KSampler                       │  Core diffusion process
│  (Denoising Loop)               │
│                                 │
│  model: [Flux 1 Dev MODEL]      │
│  positive: [CONDITIONING]       │ ← With pose control
│  negative: ["blurry, low"]      │
│  seed: [INT]                    │
│  steps: 30                      │
│  cfg: 4.0                       │ ← Guidance scale
│  sampler: "euler"               │
│  scheduler: "karras"            │
│  denoise: 1.0                   │
│                                 │
└──────────────┬──────────────────┘
               │
               ↓ (30 denoising steps)
        [LATENT] representation
               │
               ├─→ Optional: LatentUpscale
               │   (512→1024 for quality)
               │
               ↓
        ┌──────────────────┐
        │  VAEDecode       │  Convert latent to image
        │                  │
        │  samples: [LATENT] │
        │  vae: [VAE]      │
        │                  │
        └────────┬─────────┘
                 │
                 ↓
        [Generated IMAGE]
        (new appearance, same pose)


STEP 8: POST-PROCESSING ENHANCEMENT
═════════════════════════════════════
[Generated IMAGE] (512x512 or lower)
        │
        ↓
┌────────────────────────────────┐
│  ImageUpscaleWithModel         │  Increase resolution
│                                │
│  upscale_model:                │
│  "RealESRGAN_x4"               │  → 4x larger (512→2048)
│  image: [IMAGE]                │
│                                │
└────────┬─────────────────────┘
         │
         ↓
[Upscaled IMAGE] (2048x2048)
         │
         ↓
┌────────────────────────────────┐
│  ImageColorCorrection          │  Match original video colors
│                                │
│  brightness: 0.1               │
│  contrast: 1.1                 │
│  saturation: 1.0               │
│  hue_shift: 0                  │
│                                │
└────────┬─────────────────────┘
         │
         ↓
[Color-Corrected IMAGE]
         │
         ↓
┌────────────────────────────────┐
│  ImageDenoise                  │  Remove artifacts
│  (Optional)                    │
│                                │
│  strength: 0.4                 │
│                                │
└────────┬─────────────────────┘
         │
         ↓
[Denoised IMAGE]
         │
         ↓
┌────────────────────────────────┐
│  GFPGAN                        │  Enhance face details
│  (Optional but recommended)    │
│                                │
│  upscale: 2                    │
│  bg_upscale: 1                 │
│                                │
└────────┬─────────────────────┘
         │
         ↓
[Final Enhanced IMAGE]
(High quality, pose-matched)


STEP 9: REPEAT FOR ALL FRAMES
══════════════════════════════
Loop through all extracted frames (Steps 3-8):

Frame 1 → [Processing Pipeline] → Enhanced Frame 1
Frame 2 → [Processing Pipeline] → Enhanced Frame 2
Frame 3 → [Processing Pipeline] → Enhanced Frame 3
...
Frame N → [Processing Pipeline] → Enhanced Frame N

Result: [SEQUENCE of IMAGE objects] + [AUDIO object]


STEP 10: VIDEO REASSEMBLY WITH AUDIO SYNC
═════════════════════════════════════════════
[Enhanced Frames Sequence]        [Original AUDIO]
         [IMAGE list]                  [AUDIO]
                │                          │
                └──────────┬───────────────┘
                           │
                           ↓
                 ┌─────────────────────┐
                 │ VHS_VideoCombine    │
                 │                     │
                 │ images: [sequence]  │
                 │ frame_rate: 24      │ ← Match input fps
                 │ format: "h264-mp4"  │
                 │ crf: 23 (quality)   │
                 │                     │
                 └──────────┬──────────┘
                            │
                            ↓
                [VIDEO with embedded frames]
                            │
                            ↓
                 ┌─────────────────────┐
                 │ VHS_AudioCombine    │ ← Add original audio
                 │                     │
                 │ video: [VIDEO]      │
                 │ audio: [AUDIO]      │
                 │                     │
                 └──────────┬──────────┘
                            │
                            ↓
        ┌───────────────────────────────┐
        │   FINAL OUTPUT VIDEO          │
        │   • New appearance            │
        │   • Original pose/movement    │
        │   • Original audio synced     │
        │   • High quality              │
        └───────────────────────────────┘


STEP 11: SAVE OUTPUT
═════════════════════
[Final VIDEO] → ComfyUI/output/[filename].mp4

Ready for upload/distribution!
```

---

## Minimal Working Example (Simplified)

```
INPUT:
━━━━━
Video File
   │
   ↓
VHS_LoadVideo
   │
   ↓
VHS_SplitVideo ─→ Frame Images
   │
   └──→ LoadAudio ─→ Audio

PROCESS (Per Frame):
━━━━━━━━━━━━━━━━━━
Frame
   │
   ├─→ OpenPose ──→ Pose Skeleton ──→ ControlNetApply
   │                                      │
   └─→ Prompt ──→ CLIPTextEncode ────────┤
                                          │
CheckpointLoader ──→ MODEL ─────────────→ KSampler ──→ VAEDecode ──→ Image
                      CLIP
                      VAE

OUTPUT:
━━━━━━
Processed Images + Audio
   │
   ↓
VHS_VideoCombine + VHS_AudioCombine
   │
   ↓
Final Video File
```

---

## Data Type Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   DATA TYPES IN WORKFLOW                     │
└─────────────────────────────────────────────────────────────┘

INPUT TYPES:
───────────
STRING
  ├─ Video file path
  ├─ Text prompt
  ├─ Model names
  └─ Filenames

INT
  ├─ Frame rate (24, 30, 60)
  ├─ Resolution (512, 768, 1024)
  ├─ Step count (20-50)
  ├─ Seed (random number)
  └─ Strength values (0-2)

FLOAT
  ├─ CFG scale (0.0-8.0)
  ├─ ControlNet strength (0.0-2.0)
  ├─ Denoise (0.0-1.0)
  └─ Duration (seconds)


INTERNAL TYPES:
───────────────
IMAGE
  ├─ Loaded video frames
  ├─ Pose skeleton overlay
  ├─ Generated images
  ├─ Upscaled images
  └─ Final enhanced frames

CONDITIONING
  ├─ Text embeddings
  ├─ With ControlNet applied
  └─ Used by KSampler

LATENT
  ├─ Compressed representation
  ├─ Generated by KSampler
  ├─ Can be upscaled
  └─ Decoded to IMAGE

MODEL
  ├─ Flux 1 Dev weights
  ├─ Modified by LoRA
  └─ Used by KSampler

CLIP
  ├─ Text encoder
  ├─ Modified by LoRA
  └─ Used by CLIPTextEncode

VAE
  ├─ Image encoder/decoder
  ├─ Encodes images to latents
  └─ Decodes latents to images

CONTROL_NET
  ├─ Pose control model
  ├─ Applied via ControlNetApply
  └─ Guides generation

UPSCALE_MODEL
  ├─ RealESRGAN weights
  └─ Used by ImageUpscaleWithModel

AUDIO
  ├─ Audio track
  ├─ Sample rate
  ├─ Duration
  └─ Channel count

VIDEO
  ├─ Frame sequence
  ├─ Frame rate
  └─ Duration


CONVERSION FLOW:
───────────────
File → VHS_LoadVideo → VIDEO object
VIDEO → VHS_SplitVideo → IMAGE sequence
IMAGE → OpenPose → IMAGE (with skeleton)
STRING → CLIPTextEncode → CONDITIONING
CONDITIONING + IMAGE → ControlNetApply → CONDITIONING (modified)
CONDITIONING → KSampler → LATENT
LATENT → VAEDecode → IMAGE (generated)
IMAGE → ImageUpscaleWithModel → IMAGE (larger)
IMAGE sequence → VHS_VideoCombine → VIDEO
VIDEO + AUDIO → VHS_AudioCombine → VIDEO (with audio)
```

---

## Processing Pipeline Stages

```
╔════════════════════════════════════════════════════════════╗
║           GROK WORKFLOW - STAGE BREAKDOWN                  ║
╚════════════════════════════════════════════════════════════╝

STAGE 1: VIDEO IMPORT
─────────────────────
Input: MP4 file
Process: Load video file, extract frames and audio
Output: Frame sequence + Audio track
Time: <1s (I/O bound)
Nodes: VHS_LoadVideo, VHS_SplitVideo, LoadAudio


STAGE 2: POSE ANALYSIS
──────────────────────
Input: Video frames
Process: Extract skeleton/pose information
Output: Pose skeleton images
Time: 0.5-1s per frame
Nodes: OpenPose Preprocessor
Critical: Ensures poses are detected correctly


STAGE 3: PROMPT PREPARATION
───────────────────────────
Input: Original frames OR static prompt
Process: Encode text to embeddings
Output: CONDITIONING objects
Time: 0.1-0.5s
Nodes: CLIPTextEncode, QwenImageEncoder (optional)
Variation: Static vs Dynamic prompts


STAGE 4: MODEL LOADING
──────────────────────
Input: Model files from disk
Process: Load Flux 1 Dev, ControlNet, optional LoRA
Output: MODEL, CLIP, VAE, CONTROL_NET objects
Time: 5-15s (one-time)
Nodes: CheckpointLoader, ControlNetLoader, LoraLoader
Note: Happens once at workflow start


STAGE 5: CONTROLNET APPLICATION
────────────────────────────────
Input: CONDITIONING + Pose Skeleton + CONTROL_NET
Process: Merge pose control with text guidance
Output: Modified CONDITIONING
Time: 0.1s
Nodes: ControlNetApply
Critical: Balance between pose fidelity and generation freedom


STAGE 6: IMAGE GENERATION (Diffusion Loop)
────────────────────────────────────────────
Input: Modified CONDITIONING + Models + Seed
Process: Iterative denoising (30 steps typical)
Output: LATENT representation
Time: 3-8s per frame (depending on hardware)
Nodes: KSampler
Bottleneck: Most computationally expensive


STAGE 7: IMAGE DECODING
───────────────────────
Input: LATENT from KSampler
Process: VAE decoder converts latent to pixel space
Output: Generated IMAGE
Time: 0.5-1s
Nodes: VAEDecode
Note: Can optionally upscale latent first (LatentUpscale)


STAGE 8: IMAGE ENHANCEMENT
──────────────────────────
Input: Generated image
Process: Upscale, color correct, denoise, face enhance
Output: Final polished image
Time: 1-3s
Nodes: ImageUpscaleWithModel, ImageColorCorrection, ImageDenoise, GFPGAN
Quality: Critical for final output


STAGE 9: BATCH PROCESSING
──────────────────────────
Input: All generated images + audio
Process: Repeat stages 3-8 for each frame
Output: Enhanced image sequence
Time: (Per-frame time) × (Number of frames)
Example: 10s/frame × 240 frames = 40 minutes


STAGE 10: VIDEO REASSEMBLY
──────────────────────────
Input: Image sequence + Audio + Frame rate
Process: Encode frames to video, attach audio
Output: Final video file
Time: 2-5s (encoding)
Nodes: VHS_VideoCombine, VHS_AudioCombine
Verification: Sync audio with video timing


TYPICAL TIMINGS (per 1-second video segment at 24fps):
───────────────────────────────────────────────────────
Frames to process: 24 frames

Per-frame breakdown (RTX 4090):
  Stage 2 (Pose): 0.8s
  Stage 3 (Prompt): 0.2s
  Stage 5 (ControlNet): 0.1s
  Stage 6 (Generation): 5s ← Longest
  Stage 7 (Decode): 0.8s
  Stage 8 (Enhancement): 1.5s
  ────────────────────────
  Total per frame: ~8.4s

24 frames × 8.4s = 201.6 seconds (3.4 minutes per 1-second video)
For 10-second video: ~34 minutes
For 60-second video: ~3.4 hours
```

---

## Configuration Decision Tree

```
START: New Grok Workflow
        │
        ├─ Do you have adequate GPU VRAM?
        │   │
        │   ├─ YES (24GB+)
        │   │   └─→ Use flux-1-dev.safetensors (full precision)
        │   │       steps: 35-40, cfg: 4.0
        │   │
        │   └─ NO (12GB or less)
        │       └─→ Use flux-1-dev-fp8.safetensors (quantized)
        │           steps: 25-30, cfg: 4.0
        │
        ├─ Is pose matching critical?
        │   │
        │   ├─ YES (strict adherence)
        │   │   └─→ ControlNet strength: 1.5
        │   │       start: 0.0, end: 1.0
        │   │
        │   └─ MODERATE (some creativity)
        │       └─→ ControlNet strength: 1.0 (balanced)
        │           start: 0.0, end: 0.8
        │
        ├─ Do you want dynamic prompts?
        │   │
        │   ├─ YES (context-aware per frame)
        │   │   └─→ Add QwenImageEncoder
        │   │       Process: Original → Caption → Enhanced Prompt
        │   │
        │   └─ NO (fixed prompt)
        │       └─→ Use static string in PrimitiveNode
        │
        ├─ Do you need face enhancement?
        │   │
        │   ├─ YES (professional quality)
        │   │   └─→ Add GFPGAN after ImageDenoise
        │   │
        │   └─ NO (speed priority)
        │       └─→ Skip GFPGAN, use ImageDenoise only
        │
        ├─ What's your target resolution?
        │   │
        │   ├─ 4K (2160p) or display
        │   │   └─→ Generate at 512, ImageUpscaleWithModel 4x
        │   │
        │   ├─ 1080p
        │   │   └─→ Generate at 512, no upscale (or 2x)
        │   │
        │   └─ Social media (720p or less)
        │       └─→ Generate at 512 native
        │
        ├─ Audio sync required?
        │   │
        │   ├─ YES (must match original)
        │   │   └─→ LoadAudio + VHS_AudioCombine
        │   │       Verify: frame_rate = input_fps
        │   │
        │   └─ NO (separate audio)
        │       └─→ Just output video frames
        │
        └─ Need style consistency?
            │
            ├─ YES (specific look across frames)
            │   └─→ Load LoRA with strength 0.8-1.2
            │       Example: "professional_photo_lora"
            │
            └─ NO (natural variation)
                └─→ Skip LoraLoader
                    Use detailed prompts instead

END: Configured workflow ready to run
```

---

## Memory Usage Breakdown

```
Component              VRAM Usage          Notes
─────────────────────────────────────────────────────
Flux 1 Dev Model       21.4 GB (full)      or 11.3 GB (fp8)
                       11.3 GB (fp8)       ← Recommended

CLIP Encoder           ~1 GB               Text encoder

ControlNet (OpenPose)  ~2 GB               Loaded in memory

LatentUpscale          ~1 GB               Only if used

ImageUpscaleWithModel  ~2 GB               RealESRGAN 4x

GFPGAN                 ~1 GB               If face enhancement

Batch Processing       ~2 GB               Working memory

─────────────────────────────────────────────────────
TOTAL (Minimum)        ~20 GB (with fp8)   
TOTAL (Comfortable)    ~24+ GB             RTX 4090 range

For 12GB GPU: Use fp8 model + skip some enhancements
For 8GB GPU: Use fp8 + lower resolution + careful planning
```

---

*Visual diagrams created for reference during workflow building*

