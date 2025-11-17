# UGC Video Transformation - Visual Workflow Diagrams

## Complete Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UGC VIDEO TRANSFORMATION PIPELINE                    │
│                                                                          │
│  Input: Original UGC Video (Person A in Location X)                    │
│  Output: Transformed Video (Person B in Location Y, Style Z)           │
│  Constraint: Preserve all original movements and timing                 │
└─────────────────────────────────────────────────────────────────────────┘

    📹 INPUT VIDEO (60 seconds @ 30fps = 1800 frames)
         │
         ▼
    ┌──────────────┐
    │ PHASE 1      │   Extract frames + audio
    │ Video Load   │   Data: IMAGE[1800,H,W,3] + AUDIO
    └──────┬───────┘
           │
           ├────────────┐
           │            ▼
           │       ┌─────────────┐
           │       │ PHASE 2     │   Generate pose maps
           │       │ Pose Extract│   Data: IMAGE[1800,H,W,3]
           │       └──────┬──────┘
           │              │
           │              ▼
           │       ┌──────────────┐
           │       │ PHASE 3      │   Create consistent prompt
           │       │ Prompt Gen   │   Data: STRING (replicated 1800x)
           │       └──────┬───────┘
           │              │
           │              ▼
           │       ┌──────────────┐
           │       │ PHASE 4      │   Generate new frames
           │       │ Flux+CN Gen  │   Data: IMAGE[1800,H,W,3]
           │       └──────┬───────┘
           │              │
           │              ▼
           │       ┌──────────────┐
           │       │ PHASE 5      │   Reduce flickering
           │       │ Refine Pass 1│   Data: IMAGE[1800,H,W,3]
           │       └──────┬───────┘
           │              │
           │              ▼
           │       ┌──────────────┐
           │       │ PHASE 6      │   Polish details
           │       │ Refine Pass 2│   Data: IMAGE[1800,H,W,3]
           │       └──────┬───────┘
           │              │
           │              ▼
           │       ┌──────────────┐
           │       │ PHASE 7      │   Color + interpolation
           │       │ Post Process │   Data: IMAGE[1800,H,W,3]
           │       └──────┬───────┘
           │              │
           └──────────────┤
                          ▼
                   ┌──────────────┐
                   │ PHASE 8      │   Combine frames + audio
                   │ Video Export │   Data: VIDEO (H.264)
                   └──────┬───────┘
                          │
                          ▼
                  📹 FINAL VIDEO
```

## Detailed Phase Diagrams

### Phase 1-2: Input Processing

```
┌───────────────────────────────────────────────────────────────────┐
│ INPUT PROCESSING & POSE EXTRACTION                                │
└───────────────────────────────────────────────────────────────────┘

Input Video File
"gym_review.mp4"
    │
    │ [VHS Load Video Node]
    │   ├─ force_rate: 0
    │   ├─ frame_load_cap: 0
    │   └─ select_every_nth: 1
    │
    ├─────────┬─────────┬─────────┐
    │         │         │         │
    ▼         ▼         ▼         ▼
  FRAMES    AUDIO     FPS      METADATA
[1800,     [2,     30.0    {"duration": 60,
 1024,    48000*60]          "codec": "h264"}
 1024,
 3]
    │
    │ [OpenPose Preprocessor]
    │   ├─ detect_hand: true
    │   ├─ detect_body: true
    │   └─ detect_face: true
    │
    ▼
POSE MAPS (Grayscale stick figures)
[1800, 1024, 1024, 3]

Example Pose Map:
    O  ← Head
   /|\ ← Body + Arms
   / \ ← Legs
```

### Phase 3: Prompt Strategy

```
┌───────────────────────────────────────────────────────────────────┐
│ PROMPT GENERATION & CONSISTENCY                                   │
└───────────────────────────────────────────────────────────────────┘

STRATEGY A: Static Global Prompt (Simplest)
─────────────────────────────────────────────
[User Input]
"Transform to cyberpunk woman"
    │
    ▼
[Prompt Builder]
    │
    ▼
GENERATED PROMPT (Applied to ALL 1800 frames):
"A woman with long blonde hair wearing black leather jacket,
 cyberpunk style, neon purple and blue lighting,
 futuristic city background at night, detailed face,
 high quality, 8k, professional photography,
 consistent character, cinematic lighting"
    │
    ▼
[String Replicator]
    │
    ▼
PROMPT ARRAY: [prompt] * 1800 frames


STRATEGY B: Keyframe Interpolation (Advanced)
─────────────────────────────────────────────
Frame 0:    "cyberpunk woman, night, purple lighting"
Frame 600:  "cyberpunk woman, night, blue lighting"  
Frame 1200: "cyberpunk woman, dawn, pink lighting"
Frame 1800: "cyberpunk woman, day, orange lighting"
    │
    ▼
[Prompt Scheduler]
    │
    ▼
Interpolated prompts for frames 0-1800
(Gradual transition of lighting)


STRATEGY C: Character LoRA (Best Quality)
─────────────────────────────────────────────
Step 1: Generate 10 reference frames
    │
    ▼
[Train LoRA]
    │ (30-100 training steps)
    ▼
character_lora.safetensors
    │
    ▼
Step 2: Re-run with LoRA
PROMPT: "<lora:character:0.8> woman in cyberpunk city..."
    │
    ▼
Highly consistent character across all frames
```

### Phase 4: Generation with ControlNet

```
┌───────────────────────────────────────────────────────────────────┐
│ FLUX + CONTROLNET GENERATION                                      │
└───────────────────────────────────────────────────────────────────┘

[Flux.1 Dev FP8]              [Pose Maps]         [Prompt]
   12GB Model                [1800 frames]      "cyberpunk woman..."
       │                          │                     │
       │                          │                     │
       ▼                          ▼                     ▼
   [MODEL]                  [IMAGE_POSE]          [CLIP Encode]
       │                          │                     │
       │                          │                     ▼
       │                          │              [CONDITIONING]
       │                          │                     │
       │                          └─────────┬───────────┘
       │                                    │
       ▼                                    ▼
   [ApplyControlNet]  ◄───────────────────┘
   strength: 0.85
   start%: 0.0
   end%: 1.0
       │
       ▼
   [CONDITIONING_MODIFIED]
       │
       │  [Empty Latent]
       │  [30, 128, 128, 4]  ← Batch of 30 frames
       │         │
       │         ▼
       └────► [KSampler]
              steps: 25
              cfg: 7.5
              sampler: dpmpp_2m
              scheduler: karras
                 │
                 ▼
             [LATENT]
           [30, 4, 128, 128]
                 │
                 ▼
             [VAE Decode]
                 │
                 ▼
          [GENERATED FRAMES]
          [30, 1024, 1024, 3]

Note: Repeat for chunks 1-60 (1800 frames / 30 per batch)
```

### Batch Processing Strategy

```
┌───────────────────────────────────────────────────────────────────┐
│ CHUNK-BASED BATCH PROCESSING                                      │
└───────────────────────────────────────────────────────────────────┘

Total Frames: 1800 (60 seconds × 30fps)
Batch Size: 30 frames (fits in 24GB VRAM)
Overlap: 2 frames (for smooth transitions)

Chunk 1:  [0─────────29]           Process → Save
               ↓
Chunk 2:      [28──────57]         Process → Save
                   ↓
Chunk 3:          [56─────85]      Process → Save
                       ↓
...
Chunk 60:                [1771─────1800]

TRANSITION BLENDING:
─────────────────────
Chunk 1: Frames 0-29, keep frames 0-27
              ↓
         [28, 29] ← Overlap zone
              ↓
Chunk 2: Frames 28-57, keep frames 30-55
              ↓
         [56, 57] ← Overlap zone
              ↓
Chunk 3: Frames 56-85, keep frames 58-83

BLEND FUNCTION:
For overlap frames, use weighted average:
  final_frame = 0.5 * chunk_n[-2:] + 0.5 * chunk_n+1[:2]

MEMORY USAGE:
─────────────
Per chunk (30 frames, 1024x1024):
- Input frames: 30 × 1024 × 1024 × 3 × 4 bytes = 377 MB
- Pose maps: 377 MB
- Latents: 30 × 128 × 128 × 4 × 4 bytes = 7.86 MB
- Model: 12 GB (Flux FP8)
- Working memory: ~3 GB
TOTAL: ~16 GB VRAM (fits in RTX 4090)
```

### Refinement Passes

```
┌───────────────────────────────────────────────────────────────────┐
│ REFINEMENT PIPELINE                                               │
└───────────────────────────────────────────────────────────────────┘

PASS 1: Temporal Consistency
─────────────────────────────

[Generated Frames] (First pass output)
[Batch 30 frames]
    │
    │ For each frame N:
    │   Compare with frame N-1 and N+1
    │   Detect flickering regions
    │
    ▼
[Difference Map]
Highlights inconsistent pixels
    │
    ▼
[KSampler img2img mode]
├─ Input: Generated frames
├─ ControlNet: Original pose maps
├─ Prompt: Same as first pass
├─ Denoise: 0.35 (subtle changes only)
└─ Steps: 15 (faster)
    │
    ▼
[Refined Frames V1]
Smoother transitions


PASS 2: Detail Enhancement
────────────────────────────

[Refined Frames V1]
    │
    ├────────────────┐
    │                │
    ▼                ▼
OPTION A:       OPTION B:
Upscaling       Face Restoration
    │                │
    │                │
[Ultimate SD]   [CodeFormer]
Upscale         Enhance faces
    │                │
    │                │
tile: 512       fidelity: 0.7
overlap: 64         │
denoise: 0.25       │
    │                │
    └────────┬───────┘
             │
             ▼
    [Refined Frames V2]
    Higher quality


PASS 3: Post-Processing
─────────────────────────

[Refined Frames V2]
    │
    ├──► [Color Correction]
    │    ├─ Brightness: +5%
    │    ├─ Saturation: +10%
    │    └─ Contrast: +8%
    │
    ├──► [Sharpening]
    │    └─ Strength: 0.4
    │
    └──► [Frame Interpolation] (Optional)
         └─ RIFE 2x (30fps → 60fps)
              │
              ▼
         [Final Frames]
```

### Video Assembly

```
┌───────────────────────────────────────────────────────────────────┐
│ FINAL VIDEO ASSEMBLY                                              │
└───────────────────────────────────────────────────────────────────┘

[All Processed Chunks]
Chunk 1: frames_0000-0027.png
Chunk 2: frames_0030-0055.png
...
Chunk 60: frames_1770-1800.png
    │
    ▼
[Merge Chunks]
    │
    ▼
[Complete Frame Sequence]
1800 frames @ 1024x1024
    │
    ├──────────────┐
    │              │
    ▼              ▼
[Original Audio]  [FPS: 30.0]
48kHz stereo
    │              │
    └──────┬───────┘
           │
           ▼
    [VHS Combine Video]
    ├─ format: h264-mp4
    ├─ crf: 18 (high quality)
    ├─ pix_fmt: yuv420p
    └─ audio_bitrate: 320k
           │
           ▼
    Final Video Output
    "transformed_video.mp4"
    
METADATA:
├─ Resolution: 1920×1080 (if upscaled)
├─ FPS: 30
├─ Duration: 60.0s
├─ Codec: H.264
├─ Bitrate: ~10 Mbps
├─ Audio: AAC 320kbps
└─ File size: ~75 MB
```

## Node Connection Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│ COMPLETE COMFYUI NODE GRAPH                                       │
└───────────────────────────────────────────────────────────────────┘

[1: UGC Download]──video_path──►[2: VHS Load]
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                  frames           audio             fps
                    │                │                │
                    ▼                │                │
            [3: OpenPose]            │                │
                    │                │                │
                pose_maps            │                │
                    │                │                │
                    │  [4: Load Checkpoint]          │
                    │        │                       │
                    │    ┌───┴───┐                   │
                    │    │   │   │                   │
                    │  model clip vae                │
                    │    │   │                       │
                    │    │   └──►[5: CLIP Encode]    │
                    │    │        prompt:STRING      │
                    │    │            │              │
                    │    │            ▼              │
                    │    │        conditioning       │
                    │    │            │              │
                    │    │            ▼              │
                    └────┼──►[6: Apply ControlNet]   │
                         │       strength: 0.85      │
                         │            │              │
                         │            ▼              │
                         │    conditioning_modified  │
                         │            │              │
                         │            │              │
        [7: Empty Latent]◄───┐       │              │
         batch_size: 30      │       │              │
                 │           │       │              │
                 │           │       │              │
                 └───────────┴───────┴──────►[8: KSampler]
                                               steps: 25
                                               cfg: 7.5
                                                   │
                                                   ▼
                                               latent_out
                                                   │
                                                   │
                                                   ├──►[9: VAE Decode]
                                                   │        │
                                                   │        ▼
                                                   │    generated_imgs
                                                   │        │
                                                   │        │
                                                   │        ├──►[10: Refine Pass 1]
                                                   │        │         │
                                                   │        │         ▼
                                                   │        │    refined_v1
                                                   │        │         │
                                                   │        │         │
                                                   │        │         ├──►[11: Refine Pass 2]
                                                   │        │         │         │
                                                   │        │         │         ▼
                                                   │        │         │    refined_v2
                                                   │        │         │         │
                                                   │        │         │         │
                                                   │        │         │         ├──►[12: Post Process]
                                                   │        │         │         │         │
                                                   │        │         │         │         ▼
                                                   │        │         │         │    final_frames
                                                   │        │         │         │         │
                                                   └────────┴─────────┴─────────┴─────────┤
                                                            ┌────────────────────┘
                                                            │
                                                            ▼
                                                    [13: VHS Combine]◄───audio
                                                            │           fps
                                                            ▼
                                                        final.mp4
```

## Memory Layout Visualization

```
┌───────────────────────────────────────────────────────────────────┐
│ VRAM USAGE BREAKDOWN (24GB RTX 4090)                              │
└───────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Flux.1 Dev FP8 Model                         12.0 GB      │
├────────────────────────────────────────────────────────────┤
│ ControlNet Union Pro                          1.5 GB      │
├────────────────────────────────────────────────────────────┤
│ VAE                                           0.5 GB      │
├────────────────────────────────────────────────────────────┤
│ CLIP                                          0.5 GB      │
├────────────────────────────────────────────────────────────┤
│ Input Frames (30 × 1024²)                     0.4 GB      │
├────────────────────────────────────────────────────────────┤
│ Pose Maps (30 × 1024²)                        0.4 GB      │
├────────────────────────────────────────────────────────────┤
│ Latent Batch (30 × 128² × 4)                  0.008 GB    │
├────────────────────────────────────────────────────────────┤
│ Generated Frames (30 × 1024²)                 0.4 GB      │
├────────────────────────────────────────────────────────────┤
│ Working Memory (gradients, etc.)              3.0 GB      │
├────────────────────────────────────────────────────────────┤
│ ComfyUI Overhead                              1.0 GB      │
└────────────────────────────────────────────────────────────┘
TOTAL: ~19.7 GB / 24 GB Available

OPTIMIZATION STRATEGIES:
────────────────────────
If OOM (Out of Memory):
1. Reduce batch size: 30 → 20 → 10
2. Use GGUF Q5: 12GB → 6GB
3. Reduce resolution: 1024 → 768
4. Use tiled VAE
5. Enable --lowvram flag
```

## Processing Timeline

```
┌───────────────────────────────────────────────────────────────────┐
│ PROCESSING TIMELINE (60-second video, RTX 4090)                   │
└───────────────────────────────────────────────────────────────────┘

00:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Start
      │
      ├─ Load video & extract frames
00:30 ├─────────────────────────────────────────► 0.5 min
      │
      ├─ OpenPose preprocessing (1800 frames)
02:00 ├─────────────────────────────────────────► 2.0 min
      │
      ├─ Flux generation (60 chunks × 25 steps)
      │  Chunk 1: ████ 4 min
      │  Chunk 2: ████ 4 min
      │  ...
      │  Chunk 60: ████ 4 min
242:00├─────────────────────────────────────────► 240 min (4 hours)
      │
      ├─ Refinement Pass 1 (15 steps × 60 chunks)
338:00├─────────────────────────────────────────► 96 min (1.6 hours)
      │
      ├─ Refinement Pass 2 (upscale/enhance)
368:00├─────────────────────────────────────────► 30 min
      │
      ├─ Post-processing & video assembly
373:00├─────────────────────────────────────────► 5 min
      │
      ▼
TOTAL: ~6.2 hours

SPEEDUP STRATEGIES:
───────────────────
1. Skip refinement passes: 6.2h → 4.0h (35% faster)
2. Reduce steps (25→20): 4.0h → 3.2h (20% faster)
3. Process keyframes only (1/10): 3.2h → 0.3h (90% faster)
4. Use Euler sampler: 3.2h → 2.8h (12% faster)
5. Lower resolution (768px): 3.2h → 2.0h (38% faster)

BEST COMPROMISE:
768px, 20 steps, DPM++ 2M, no refinement: ~1.5 hours
```

## Quality vs Performance Matrix

```
┌───────────────────────────────────────────────────────────────────┐
│ QUALITY VS PERFORMANCE TRADEOFFS                                  │
└───────────────────────────────────────────────────────────────────┘

                      QUALITY
                        ↑
                        │
  ████████████████      │       Settings:
  █  MAXIMUM   █       │       • 1024×1024
  █  QUALITY   █       │       • 30 steps
  ████████████████      │       • DPM++ 2M Karras
        │              │       • 2 refinement passes
        │              │       • ControlNet 0.9
        ├──────────────┤       Time: 6 hours
        │              │
   ███████████         │       Settings:
   █ HIGH    █         │       • 1024×1024
   █ QUALITY █         │       • 25 steps
   ███████████         │       • DPM++ 2M
        │              │       • 1 refinement pass
        │              │       • ControlNet 0.85
        ├──────────────┤       Time: 4 hours ⭐ RECOMMENDED
        │              │
    ██████             │       Settings:
    █GOOD█             │       • 768×768
    ██████             │       • 20 steps
        │              │       • DPM++ 2M
        │              │       • No refinement
        ├──────────────┤       • ControlNet 0.8
        │              │       Time: 1.5 hours
     ███               │
     █ FAST            │       Settings:
     ███               │       • 512×512
        │              │       • 15 steps
        │              │       • Euler
        └──────────────┴───────• ControlNet 0.75
                               Time: 0.5 hours
         ◄────────────────────►
              SPEED
```

## Alternative Workflow: AnimateDiff

```
┌───────────────────────────────────────────────────────────────────┐
│ ANIMATEDIFF APPROACH (Simplified)                                 │
└───────────────────────────────────────────────────────────────────┘

Traditional Frame-by-Frame:
[Frame 1] → Generate → [Output 1]
[Frame 2] → Generate → [Output 2]  
[Frame 3] → Generate → [Output 3]
...
Problem: Each frame independent → flickering

AnimateDiff Approach:
[Frames 1-16] → Generate with temporal attention → [Outputs 1-16]
              Motion Module ensures consistency

WORKFLOW:
─────────
[Video Input]
     │
     ▼
[Extract Frames]
     │
     ▼
[OpenPose Sequence]
pose_0, pose_1, ..., pose_15
     │
     ▼
[AnimateDiff Sampler]
├─ Context: 16 frames
├─ Motion Module: v3
├─ ControlNet: OpenPose batch
└─ Prompt: "cyberpunk woman..."
     │
     ▼
[16 Consistent Frames]
     │
     ▼
Slide window by 8 frames (50% overlap)
Process frames 8-23, 16-31, etc.
     │
     ▼
[Complete Video]

ADVANTAGES:
✓ Better temporal consistency
✓ Smoother motion
✓ Faster (fewer total generations)

DISADVANTAGES:
✗ Max 16-24 frame context
✗ Requires AnimateDiff-compatible model
✗ Less control over individual frames
```

## Error Recovery Flow

```
┌───────────────────────────────────────────────────────────────────┐
│ ERROR HANDLING & RECOVERY                                         │
└───────────────────────────────────────────────────────────────────┘

[Processing Chunk 23/60]
         │
         ▼
    ┌─────────┐
    │ ERROR?  │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    ▼         ▼
[Identify]  [Continue]
    │
    ├─► Out of Memory?
    │   └─► Reduce batch size
    │       Retry chunk
    │
    ├─► Generation failed?
    │   └─► Re-roll seed
    │       Retry with new seed
    │
    ├─► Pose detection failed?
    │   └─► Use previous pose
    │       Or skip frame
    │
    └─► ComfyUI crash?
        └─► Save progress
            Resume from last chunk
            
CHECKPOINT SYSTEM:
──────────────────
After each chunk:
1. Save processed frames
2. Update progress.json:
   {
     "completed_chunks": 23,
     "total_chunks": 60,
     "last_chunk_file": "frames_23.png"
   }
3. Can resume if interrupted
```

