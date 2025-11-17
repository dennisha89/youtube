# ComfyUI Workflow Guide - UGC Video Transformation

## Quick Start

You now have **2 working ComfyUI workflow files** ready to load!

### Files Created

1. **`ugc_basic_starter.json`** - Simple workflow to get started
2. **`ugc_video_transformation_complete.json`** - Full workflow with post-processing

---

## How to Use These Workflows

### Step 1: Install Required Extensions

Open ComfyUI Manager and install:

```bash
# Required Extensions:
1. ComfyUI-VideoHelperSuite (VHS)
2. comfyui_controlnet_aux (ControlNet Preprocessors)
```

Or install manually:
```bash
cd ComfyUI/custom_nodes/

# Video Helper Suite
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git

# ControlNet Preprocessors
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git

# Install dependencies
cd ComfyUI-VideoHelperSuite && pip install -r requirements.txt
cd ../comfyui_controlnet_aux && pip install -r requirements.txt
```

### Step 2: Download Required Models

Place these in `ComfyUI/models/`:

**Checkpoints** (`ComfyUI/models/checkpoints/`):
- **Flux 1 Dev FP8** (11.3 GB)
  - Download: https://huggingface.co/Comfy-Org/flux1-dev/blob/main/flux1-dev-fp8.safetensors

**ControlNet** (`ComfyUI/models/controlnet/`):
- **OpenPose FP16** (2.1 GB)
  - Download: https://huggingface.co/lllyasviel/ControlNet-v1-1/blob/main/control_v11p_sd15_openpose.pth
  - Rename to: `control_openpose-fp16.safetensors`

**Upscale Models** (`ComfyUI/models/upscale_models/`) - For complete workflow only:
- **RealESRGAN x4** (65 MB)
  - Download: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
  - Rename to: `RealESRGAN_x4.pth`

### Step 3: Load the Workflow

1. **Open ComfyUI** → http://127.0.0.1:8188
2. **Click "Load"** button (top menu)
3. **Navigate to:**
   ```
   ComfyUI/custom_nodes/ComfyUI-UGC-Video-Generator/workflows/
   ```
4. **Choose:**
   - `ugc_basic_starter.json` - Start here!
   - `ugc_video_transformation_complete.json` - After you understand basics

### Step 4: Configure the Workflow

#### A. Set Input Video

**Node 1: VHS_LoadVideo**
- Click on the node
- Click "Choose File" or enter path
- Example: `input.mp4` (place in `ComfyUI/input/`)

#### B. Customize the Transformation

**Node 4: CLIPTextEncode (Positive Prompt)**

Change this to describe what you want:

**Original:**
```
professional female fitness influencer, athletic build, wearing modern sportswear,
reviewing protein powder in bright modern gym, natural lighting, enthusiastic
expression, holding protein container, 4k quality, detailed
```

**Examples to try:**

*Change gender:*
```
professional male bodybuilder, muscular build, wearing tank top,
reviewing protein powder in home gym, natural lighting, confident
expression, holding protein container, 4k quality, detailed
```

*Change setting:*
```
young woman, casual clothing, reviewing protein powder in modern
kitchen, bright daylight through windows, friendly smile,
holding protein container, 4k quality, detailed
```

*Change style:*
```
fitness model, professional attire, presenting protein powder in
luxury penthouse, golden hour lighting, sophisticated expression,
holding protein container, cinematic, 4k quality, detailed
```

#### C. Adjust ControlNet Strength

**Node 7: ControlNetApply**

- **Value: 0.8** (default, balanced)
- **0.7-0.75**: More creative freedom, less exact pose matching
- **0.8-0.85**: Balanced (recommended for most cases)
- **0.9-0.95**: Very strict pose preservation (for dance, sports)

#### D. Adjust Generation Settings

**Node 9: KSampler**

- **Steps: 20** (good balance, can go 15 for faster / 30 for better)
- **CFG: 7.0** (prompt strength, 6-8 recommended)
- **Denoise: 0.75** (transformation strength)
  - 0.5-0.6: Minor changes
  - 0.7-0.8: Moderate transformation (recommended)
  - 0.9-1.0: Major changes

### Step 5: Run the Workflow

1. **Click "Queue Prompt"** (top right)
2. **Wait for processing** (check console for progress)
3. **Find output** in `ComfyUI/output/`

---

## Workflow Comparison

### Basic Starter (`ugc_basic_starter.json`)

**What it does:**
- Load video → Extract poses → Transform frames → Output video

**Pros:**
- ✅ Faster (no post-processing)
- ✅ Simpler to understand
- ✅ Less VRAM required
- ✅ Good for testing/iteration

**Cons:**
- ❌ No upscaling
- ❌ No face enhancement
- ❌ Lower final quality

**Processing time:**
- RTX 4090: ~3 sec/frame
- RTX 3090: ~5 sec/frame
- RTX 3060: ~8 sec/frame

**Use when:**
- Learning the workflow
- Testing different prompts quickly
- Don't need highest quality
- Working with lower-end GPU

---

### Complete (`ugc_video_transformation_complete.json`)

**What it does:**
- Everything in Basic +
- Upscale 4x with RealESRGAN
- Sharpen details
- Face enhancement with GFPGAN
- Color correction

**Pros:**
- ✅ Highest quality output
- ✅ 4x resolution increase
- ✅ Better faces
- ✅ Professional results

**Cons:**
- ❌ Slower processing
- ❌ More VRAM needed
- ❌ More complex

**Processing time:**
- RTX 4090: ~6-8 sec/frame
- RTX 3090: ~10-12 sec/frame
- RTX 3060: ~15-20 sec/frame

**Use when:**
- Creating final output
- Need highest quality
- Have powerful GPU
- Willing to wait longer

---

## Troubleshooting

### "Node not found" errors

**Problem:** ComfyUI can't find VHS or ControlNet nodes

**Solution:**
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
# Restart ComfyUI
```

### "Model not found" errors

**Problem:** Missing Flux or ControlNet model

**Solution:**
1. Check model files are in correct folders:
   - `ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors`
   - `ComfyUI/models/controlnet/control_openpose-fp16.safetensors`
2. Refresh ComfyUI page
3. Check model dropdown shows the files

### Out of memory errors

**Problem:** GPU runs out of VRAM

**Solutions:**
1. **Use Basic workflow** (less memory)
2. **Reduce resolution** in VHS_LoadVideo node
3. **Lower batch size** (process fewer frames at once)
4. **Use FP8 models** (already recommended)
5. **Enable `--lowvram` flag:**
   ```bash
   python main.py --lowvram
   ```

### Pose not being preserved

**Problem:** Generated frames don't match original movement

**Solutions:**
1. **Increase ControlNet strength** to 0.9-0.95
2. **Check OpenPose output** - should show skeleton overlay
3. **Lower denoise** to 0.6-0.7
4. **Increase CFG** to 8-10

### Character inconsistency between frames

**Problem:** Person looks different in each frame

**Solutions:**
1. **Use more descriptive prompt:**
   ```
   same woman throughout, consistent face, 25 years old, long brown hair,
   athletic build, wearing red tank top...
   ```
2. **Lower denoise** to 0.6-0.7
3. **Add LoRA** trained on reference character (advanced)
4. **Use IP-Adapter** for face consistency (requires additional nodes)

### Video output has no audio

**Problem:** Final video is silent

**Solutions:**
1. Check audio link from VHS_LoadVideo to VHS_VideoCombine (link 15)
2. Make sure "Audio Enable" is checked in VHS_VideoCombine
3. Check input video actually has audio

### Slow processing

**Problem:** Taking too long per frame

**Solutions:**
1. **Use Basic workflow**
2. **Reduce steps** to 15 in KSampler
3. **Lower resolution** in video loading
4. **Disable post-processing nodes** (right-click → Bypass)
5. **Process keyframes only** (every 5-10 frames)

---

## Example Transformation Scenarios

### Scenario 1: Gender Swap

**Original:** Male reviewing protein powder

**Positive Prompt:**
```
athletic young woman, ponytail, wearing sports bra and leggings,
reviewing protein powder in home gym, natural lighting, enthusiastic
smile, holding protein container, fit physique, professional photo, 4k
```

**Settings:**
- ControlNet: 0.85 (preserve pose well)
- Denoise: 0.8 (moderate transformation)
- Steps: 25

### Scenario 2: Background Change

**Original:** Review in messy room

**Positive Prompt:**
```
same person, modern minimalist home gym, white walls, plants in
background, large windows with natural light, wooden floor, clean
aesthetic, professional photo, 4k quality
```

**Settings:**
- ControlNet: 0.8
- Denoise: 0.75
- Focus prompt on environment

### Scenario 3: Style Transfer

**Original:** Casual review

**Positive Prompt:**
```
professional fitness influencer, studio lighting setup, three-point
lighting, cinematic look, color graded, professional production,
expensive camera, shallow depth of field, bokeh background, 4k
```

**Settings:**
- ControlNet: 0.75 (allow some variation)
- Denoise: 0.85
- Steps: 30

### Scenario 4: Age Change

**Original:** Young person (20s)

**Positive Prompt:**
```
mature fitness expert, 45 years old, distinguished appearance, gray
hair, experienced look, professional attire, reviewing protein powder
in upscale gym, confident expression, 4k quality
```

**Settings:**
- ControlNet: 0.8
- Denoise: 0.8
- May need face enhancement in post

### Scenario 5: Clothing Change

**Original:** Tank top and shorts

**Positive Prompt:**
```
same person, wearing professional business casual outfit, button-down
shirt, presenting product in office environment, natural window
lighting, professional demeanor, 4k quality
```

**Settings:**
- ControlNet: 0.85 (preserve body pose)
- Denoise: 0.75
- Focus on clothing description

---

## Optimization Tips

### For Faster Processing

1. **Lower resolution:** 512px or 768px in VHS_LoadVideo
2. **Reduce steps:** 15 instead of 20 in KSampler
3. **Skip post-processing:** Use Basic workflow
4. **Process every Nth frame:** Load with frame skip in VHS
5. **Use Euler sampler:** Fastest option

### For Better Quality

1. **Higher resolution:** 1024px in VHS_LoadVideo
2. **More steps:** 25-30 in KSampler
3. **Use Complete workflow:** All post-processing enabled
4. **Add detail:** More descriptive prompts
5. **Use DPM++ sampler:** Better quality, slower

### For Consistency

1. **Detailed character description:** Age, hair, build, clothing
2. **Add "consistent" keywords:** "same person throughout"
3. **Lower denoise:** 0.6-0.7 for less variation
4. **Higher ControlNet:** 0.85-0.9
5. **Consider LoRA:** Train on reference character

---

## Next Steps

1. **Start with Basic workflow** - Learn how it works
2. **Test different prompts** - Understand transformation control
3. **Try Complete workflow** - See quality difference
4. **Experiment with settings** - Find your sweet spot
5. **Process full videos** - Create real variations
6. **Share results** - Show what you've made!

---

## Support & Resources

**Documentation:**
- `VIDEO_TRANSFORMATION_README.md` - Overview
- `UGC_VIDEO_TRANSFORMATION_ARCHITECTURE.md` - Technical details
- `IMPLEMENTATION_EXAMPLES.md` - More examples

**Need help?**
- Check troubleshooting section above
- Review node configurations
- Test with short clips first (5-10 seconds)

---

**You now have everything you need to start transforming UGC videos!**

Load `ugc_basic_starter.json` in ComfyUI and experiment with your first transformation.
