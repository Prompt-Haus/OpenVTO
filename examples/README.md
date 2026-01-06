# OpenVTO Examples

Runnable examples demonstrating OpenVTO's virtual try-on capabilities.

## Prerequisites

```bash
pip install openvto
export GOOGLE_API_KEY="your-api-key"
```

Or use `--mock` flag to test without API keys.

## Examples

### 01_avatar — Avatar Generation

Generate a studio-quality avatar from a selfie and full-body posture image.

**Python script:**
```bash
python examples/01_avatar.py \
    --selfie path/to/selfie.jpg \
    --posture path/to/fullbody.jpg \
    --output avatar.png \
    --background studio
```

**Jupyter notebook:** `01_avatar.ipynb` — Interactive walkthrough with visualizations.

### 02_tryon_static.py — Static Try-On

Place clothing on an avatar image.

```bash
python examples/02_tryon_static.py \
    --avatar avatar.png \
    --clothes shirt.jpg pants.jpg \
    --output tryon.png
```

### 03_videoloop.py — Video Loop

Generate an animated video loop from a static image.

```bash
python examples/03_videoloop.py \
    --image tryon.png \
    --mode 360 \
    --seconds 4 \
    --output video.mp4
```

Modes:
- `360` — Subtle rotation animation
- `idle` — Breathing/micro-movements

### 04_full_pipeline.py — End-to-End

Run the complete pipeline: avatar → try-on → video.

```bash
python examples/04_full_pipeline.py \
    --selfie selfie.jpg \
    --posture fullbody.jpg \
    --clothes shirt.jpg pants.jpg \
    --output-dir ./output
```

### 05_batch_outfits.py — Multiple Outfits

Process multiple outfits on a single avatar.

```bash
python examples/05_batch_outfits.py \
    --avatar avatar.png \
    --outfits "shirt.jpg,pants.jpg" "dress.jpg" "jacket.jpg,jeans.jpg" \
    --output-dir ./batch_output
```

## Testing Without API Keys

All examples support `--mock` flag for testing:

```bash
python examples/04_full_pipeline.py \
    --selfie test.jpg \
    --posture test.jpg \
    --clothes test.jpg \
    --mock
```

This generates placeholder outputs without calling real APIs.

