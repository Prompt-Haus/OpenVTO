![OpenVTO Header](openvto-header.jpg)

# OpenVTO

**OpenVTO** is an open-source toolkit for building studio-quality virtual try-ons with generative AI, both as high-end still photos and short animated loops.

It provides a stable and consistent workflow for generating clean "studio avatar" images, swapping outfits from product images, and optionally turning the result into a 4-8s motion clip using image-to-video models.

OpenVTO is designed for **speed**, **consistency**, and **aesthetics**: uniform lighting, controlled backgrounds, repeatable outputs that feel like a premium fashion app.

---

## Monorepo Structure

```
OpenVTO/
├── packages/
│   └── sdk/                 # Python SDK (pip install openvto)
├── apps/
│   ├── api/                 # FastAPI server
│   └── playground/          # React Native mobile app
├── examples/                # Jupyter notebooks & examples
├── package.json             # Root package.json (pnpm workspaces)
├── pnpm-workspace.yaml      # Workspace configuration
└── turbo.json               # Turborepo configuration
```

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

### SDK Only

```bash
pip install openvto
```

### Full Monorepo Development

```bash
# Clone the repository
git clone https://github.com/Prompt-Haus/OpenVTO.git
cd OpenVTO

# Install Node.js dependencies (for playground)
pnpm install

# Install Python SDK in development mode
cd packages/sdk
pip install -e ".[dev]"

# Install API dependencies
cd ../../apps/api
pip install -e ".[dev]"
```

---

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

---

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

## Running the Apps

### API Server

```bash
# From repository root
pnpm api

# Or directly
cd apps/api
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Mobile Playground

```bash
# From repository root
pnpm playground dev

# Or directly
cd apps/playground
pnpm dev
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
import openvto.example as example

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

## Development

### Running Tests

```bash
# SDK tests
cd packages/sdk
pytest

# Or from root
pnpm sdk:test
```

### Linting

```bash
# SDK
pnpm sdk:lint

# Playground
pnpm playground lint

# Format TypeScript/JavaScript
pnpm format
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Third-Party Services & Trademarks

OpenVTO integrates with Google Cloud's Generative AI services. By using this library with Google's APIs, you agree to comply with (not limited to):

- [Google Cloud Terms of Service](https://cloud.google.com/terms)
- [Google's Generative AI Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy)
- [Vertex AI Terms of Service](https://cloud.google.com/terms/service-terms)

**Trademark Notice:** Google, Google Cloud, Vertex AI, Gemini, and Veo are trademarks of Google LLC. OpenVTO is an independent open-source project and is not affiliated with, endorsed by, or sponsored by Google LLC.

---

## Data Privacy & Usage Disclaimer

**⚠️ Important:** OpenVTO processes personal images including selfies and full-body photographs. By using this library, you acknowledge and agree that:

1. **User Consent:** You are solely responsible for obtaining all necessary rights, permissions, and consents from individuals whose images are processed. This includes explicit consent for:
   - Collection and processing of biometric data (facial features, body shape)
   - Generation of synthetic/AI-generated images based on their likeness
   - Any commercial or public use of generated content

2. **Data Handling:** Images uploaded to this library may be sent to third-party AI services (e.g., Google Vertex AI) for processing. Review and comply with the data processing terms of these services.

3. **No Warranty:** This software is provided "AS IS" without warranty of any kind. The authors and contributors are not liable for any claims, damages, or other liability arising from use of this software.

4. **Prohibited Uses:** Do not use this library to:
   - Create non-consensual intimate imagery
   - Generate content for harassment, fraud, or deception
   - Impersonate individuals without their consent
   - Violate any applicable laws or regulations

5. **Regulatory Compliance:** This library is not designed for, and should not be used in, regulated industries (healthcare, finance, legal) without appropriate professional guidance and compliance measures.

---

## Demo Assets License

The demo assets in `openvto/assets/` are provided for **testing and demonstration purposes only**.

| Asset Type | Source | License |
|------------|--------|---------|
| Avatar images | AI-generated by OpenVTO team | MIT License |
| Clothing images | AI-generated by OpenVTO team | MIT License |
| People images | AI-generated by OpenVTO team | MIT License |

These assets are synthetic/AI-generated and do not depict real individuals. They are released under the same MIT license as the rest of this project and may be used freely for testing, development, and demonstration.

**Note:** When using OpenVTO in production, you should use your own properly licensed assets and ensure compliance with all applicable image rights and privacy laws.

---

## Contact

This is free and open source project. If you need to build something custom in your company reach out to creators: https://www.linkedin.com/in/drozdmatt/ and https://www.linkedin.com/in/widlarz/. 

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

For information about third-party dependencies and their licenses, see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
