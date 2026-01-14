# OpenVTO SDK

Open-source toolkit for building studio-quality virtual try-ons with generative AI.

## Installation

```bash
pip install openvto
```

## Quick Start

```python
from openvto import OpenVTO

# Initialize client
vto = OpenVTO(provider="google")

# Generate avatar from selfie + posture
avatar = vto.generate_avatar(
    selfie="selfie.jpg",
    posture="fullbody.jpg"
)

# Try on clothes
tryon = vto.generate_tryon(
    avatar=avatar,
    clothes=["shirt.jpg", "pants.jpg"]
)

# Generate video loop
video = vto.generate_videoloop(tryon.image)
```

## Documentation

See the main [README](../../README.md) for full documentation.

## License

MIT

