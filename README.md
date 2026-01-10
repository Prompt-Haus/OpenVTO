![OpenVTO Header](openvto-header.jpg)

# OpenVTO

**OpenVTO** is an open-source toolkit for building studio-quality virtual try-ons with generative AI, both as high-end still photos and short animated loops.

It provides a stable and consistent workflow for generating clean "studio avatar" images, swapping outfits from product images, and optionally turning the result into a 4-8s motion clip using image-to-video models.

OpenVTO is designed for **speed**, **consistency**, and **aesthetics**: uniform lighting, controlled backgrounds, repeatable outputs that feel like a premium fashion app.

---

## Goal

OpenVTO's goal is simple: **make it easy for teams to ship virtual try-ons that look good enough to market, not just "tech demos."**

---

## What OpenVTO Includes

| Feature | Description |
|---------|-------------|
| **Avatar Generation** | Generate studio-quality avatars from 2 photos (selfie and posture) with controlled lighting and backgrounds |
| **Virtual Try-On** | Garment swap from catalog images — single items or complete outfits |
| **Video Loop Generation** | Animated try-ons as loop-friendly 4–8s clips using image-to-video models |
| **Prompt Presets & Guardrails** | Keep identity, body shape, and style consistent across generations |
| **Example Implementations** | Just Jupyter notebooks with code and visualizations |

---

## Installation

```bash
pip install openvto
```

## Google Vertex AI Setup

1. Set up a Google Cloud project and enable the Vertex AI API.
2. Create a service account and download the JSON key file.
3. Set the following environment variables:

```bash
export GOOGLE_SERVICE_ACCOUNT_KEY="path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

## Quick Start

```python
import openvto

# Initialize the client (uses Google Vertex AI by default)
vto = openvto.OpenVTO()

# 1. Generate a studio-quality avatar from selfie + posture photos
avatar = vto.generate_avatar(
    selfie="selfie.jpg",
    posture="posture.jpg",
    return_type="pil"
)

# 2. Apply clothing items to the avatar
tryon = vto.generate_tryon(
    avatar=avatar,
    clothes=["jacket.jpg", "pants.jpg", "shirt.jpg"],
    return_type="pil"
)

# 3. Generate an animated video loop
video = vto.generate_videoloop(
    static_image=tryon,
    mode="turn_360",
    return_type="b64"
)
```

---

## Pipelines

### Avatar Generation

Generate a studio-quality avatar from input photos. Requires a selfie (for identity) and a posture image (for pose reference).

```python
avatar = vto.generate_avatar(
    selfie=selfie_image,
    posture=posture_image
)
```

### Virtual Try-On

Apply clothing items to an avatar. Accepts a list of garment images (front views).

```python
tryon = vto.generate_tryon(
    avatar=avatar,
    clothes=[jacket, pants, shirt]
)
```

### Video Loop Generation

Turn a static try-on result into an animated 4-8s video loop.

```python
video = vto.generate_videoloop(
    static_image=tryon,
    mode="turn_360"
)
```

---

## Models

OpenVTO uses these models from Google Vertex AI by default:

| Model | Purpose |
|-------|---------|
| `gemini-3-pro-image-preview` | High-quality image generation |
| `veo-3.1-fast-generate-preview` | Cost-effective video generation |

---

## Example Assets

OpenVTO includes bundled demo assets for quick testing and prototyping. Access them via the `openvto.example` module:

```python
from openvto.example import example

# Get all items in a category
all_jackets = example.clothes("jackets")
# [{'i': 1, 'front': Path(...), 'back': Path(...)}, ...]

# Get a specific item (both views)
jacket = example.clothes("jackets", i=2)
# {'front': Path('.../2_front.jpg'), 'back': Path('.../2_back.jpg')}

# Get a specific view
front_path = example.clothes("jackets", i=2, view="front")
# Path('.../2_front.jpg')

# Get an avatar image
avatar_path = example.avatar(i=1)
# Path('.../1.png')

# Get a person photo (posture or selfie)
posture_path = example.person(i=1, kind="posture")
selfie_path = example.person(i=1, kind="selfie")
```

### Available Assets

| Category | Items | Views |
|----------|-------|-------|
| `jackets` | 1-4 | front, back |
| `pants` | 1-4 | front, back |
| `shirts` | 1-4 | front, back |
| `avatars` | 1 | - |
| `people` | 1 | posture, selfie |

### Return Types

By default, functions return `pathlib.Path` objects. You can also request:

```python
# Get raw bytes
data = example.clothes("jackets", i=1, view="front", return_type="bytes")

# Get PIL Image (requires pillow: pip install openvto[examples])
img = example.clothes("jackets", i=1, view="front", return_type="pil")
```

---

## FastAPI Example

OpenVTO includes a FastAPI example server. To run it, use the following command:

```bash
uvicorn fastapi.app.main:app --reload
```

Then, you can access the API at `http://localhost:8000`.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is open source. See the [LICENSE](LICENSE) file for details.
