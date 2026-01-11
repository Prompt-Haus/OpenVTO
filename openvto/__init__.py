"""OpenVTO - Open-source toolkit for studio-quality virtual try-ons with generative AI."""

__version__ = "0.1.4"

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

# Import example submodule for convenient access via openvto.example
from openvto import example

__all__ = [
    "OpenVTO",
    "__version__",
    "example",
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
