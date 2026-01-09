"""OpenVTO - Open-source toolkit for studio-quality virtual try-ons with generative AI."""

__version__ = "0.1.0"

from openvto.client import OpenVTO
from openvto.types import (
    Avatar,
    AvatarResult,
    Background,
    ClothingItem,
    GenerationMeta,
    ImageInput,
    ImageModel,
    Outfit,
    PipelineResult,
    TryOnResult,
    TryOnVariant,
    VideoLoopMode,
    VideoLoopResult,
    VideoModel,
)

__all__ = [
    "OpenVTO",
    "__version__",
    # Types
    "Avatar",
    "AvatarResult",
    "Background",
    "ClothingItem",
    "GenerationMeta",
    "ImageInput",
    "ImageModel",
    "Outfit",
    "PipelineResult",
    "TryOnResult",
    "TryOnVariant",
    "VideoLoopMode",
    "VideoLoopResult",
    "VideoModel",
]
