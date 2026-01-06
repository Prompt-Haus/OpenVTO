"""Core data models for OpenVTO."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import BinaryIO, Union

# Type alias for flexible image input
ImageInput = Union[str, Path, bytes, BinaryIO, "PILImage"]

# Placeholder for PIL.Image.Image to avoid hard dependency
try:
    from PIL.Image import Image as PILImage
except ImportError:
    PILImage = None  # type: ignore[misc, assignment]


class ImageModel(str, Enum):
    """Supported image generation models."""

    NANO_BANANA = "gemini-2.5-flash-image"
    NANO_BANANA_PRO = "gemini-3-pro-image-preview"


class VideoModel(str, Enum):
    """Supported video generation models."""

    VEO_31 = "veo-3.1"
    VEO_31_FAST = "veo-3.1-fast"


class VideoLoopMode(str, Enum):
    """Video loop animation modes."""

    TURN_360 = "360"  # Subtle 360° turn
    IDLE = "idle"  # Breathing/idle motion


class Background(str, Enum):
    """Predefined background styles."""

    STUDIO = "studio"
    WHITE = "white"
    GRADIENT = "gradient"
    CUSTOM = "custom"


@dataclass
class ClothingItem:
    """A single clothing item for virtual try-on.

    Attributes:
        id: Unique identifier for the item.
        image: Image of the clothing item (path, URL, bytes, or PIL Image).
        description: Optional description (e.g., "oversized linen shirt").
        category: Optional category (e.g., "top", "bottom", "dress").
        tags: Optional tags for filtering/grouping.
    """

    id: str
    image: ImageInput
    name: str | None = None
    description: str | None = None
    styling: str | None = None
    category: str | None = None


@dataclass
class Outfit:
    """A complete outfit composed of one or more clothing items.

    Attributes:
        items: List of clothing items that make up the outfit.
        name: Optional name for the outfit.
    """

    items: list[ClothingItem]
    name: str | None = None

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("Outfit must contain at least one clothing item")


@dataclass
class GenerationMeta:
    """Metadata about a generation request.

    Attributes:
        model: The model used for generation.
        provider: The provider used (e.g., "google", "mock").
        seed: Random seed used for reproducibility.
        latency_ms: Generation time in milliseconds.
        cache_hit: Whether the result was served from cache.
        cache_key: The cache key used for this generation.
        prompt: The prompt used for generation.
        prompt_version: Version identifier for the prompt template.
    """

    model: str
    provider: str
    seed: int | None = None
    latency_ms: float | None = None
    cache_hit: bool = False
    cache_key: str | None = None
    prompt: str | None = None
    prompt_version: str | None = None


@dataclass
class Avatar:
    """A generated avatar base image.

    Attributes:
        image: The avatar image data (bytes or path).
        width: Image width in pixels.
        height: Image height in pixels.
        background: Background style used.
        meta: Generation metadata.
    """

    image: bytes
    width: int
    height: int
    background: Background = Background.STUDIO
    meta: GenerationMeta | None = None


@dataclass
class AvatarResult:
    """Result from avatar generation.

    Attributes:
        avatar: The generated avatar.
        selfie_hash: Hash of the input selfie for caching.
        posture_hash: Hash of the input posture image for caching.
    """

    avatar: Avatar
    selfie_hash: str | None = None
    posture_hash: str | None = None

    @property
    def image(self) -> bytes:
        """Convenience accessor for avatar image bytes."""
        return self.avatar.image

    @property
    def meta(self) -> GenerationMeta | None:
        """Convenience accessor for generation metadata."""
        return self.avatar.meta


@dataclass
class TryOnVariant:
    """A single try-on variant result.

    Attributes:
        image: The generated try-on image (bytes).
        meta: Generation metadata for this variant.
    """

    image: bytes
    meta: GenerationMeta | None = None


@dataclass
class TryOnResult:
    """Result from try-on generation.

    Attributes:
        try_on: The generated try-on variant.
        avatar_hash: Hash of the input avatar for caching.
        clothing_hash: Hash of the clothing composite for caching.
    """

    try_on: TryOnVariant
    avatar_hash: str | None = None
    clothing_hash: str | None = None

    @property
    def image(self) -> bytes:
        """Convenience accessor for the try-on's image."""
        return self.try_on.image

    @property
    def meta(self) -> GenerationMeta | None:
        """Convenience accessor for the try-on's metadata."""
        return self.try_on.meta


@dataclass
class VideoLoopResult:
    """Result from video loop generation.

    Attributes:
        video: The generated video data (bytes).
        first_frame: The first frame of the video (bytes).
        last_frame: The last frame of the video (bytes).
        duration_seconds: Duration of the video in seconds.
        width: Video width in pixels.
        height: Video height in pixels.
        mode: The loop mode used.
        meta: Generation metadata.
    """

    video: bytes
    first_frame: bytes
    last_frame: bytes
    duration_seconds: float
    width: int
    height: int
    mode: VideoLoopMode = VideoLoopMode.TURN_360
    meta: GenerationMeta | None = None


@dataclass
class PipelineResult:
    """Result from a full pipeline run (avatar → try-on → video).

    Attributes:
        avatar: The generated avatar result.
        tryon: The try-on result (if generated).
        video: The video loop result (if generated).
        total_latency_ms: Total pipeline execution time in milliseconds.
    """

    avatar: AvatarResult
    tryon: TryOnResult | None = None
    video: VideoLoopResult | None = None
    total_latency_ms: float | None = None

    @property
    def static_image(self) -> bytes:
        """Get the final static image (try-on if available, else avatar)."""
        if self.tryon:
            return self.tryon.image
        return self.avatar.image

    @property
    def has_video(self) -> bool:
        """Check if video was generated."""
        return self.video is not None
