"""OpenVTO - Open-source toolkit for studio-quality virtual try-ons with generative AI."""

__version__ = "0.0.1"

from openvto.client import OpenVTO
from openvto.types import (
    Avatar,
    AvatarResult,
    ClothingItem,
    GenerationMeta,
    ImageInput,
    Outfit,
    PipelineResult,
    TryOnResult,
    VideoLoopResult,
)

__all__ = [
    "OpenVTO",
    "__version__",
    # Types
    "Avatar",
    "AvatarResult",
    "ClothingItem",
    "GenerationMeta",
    "ImageInput",
    "Outfit",
    "PipelineResult",
    "TryOnResult",
    "VideoLoopResult",
]
