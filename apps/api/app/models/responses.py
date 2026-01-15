"""Pydantic response models."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str


class ClothingCategoriesResponse(BaseModel):
    """List of clothing categories."""

    categories: list[str]


class ClothingItemsResponse(BaseModel):
    """Items in a clothing category."""

    category: str
    indices: list[int]
    views: list[str]


class GenerationMetaResponse(BaseModel):
    """Metadata about a generation request."""

    model: str
    provider: str
    latency_ms: float | None
    seed: int | None


class AvatarResponse(BaseModel):
    """Avatar generation response."""

    image_b64: str
    width: int
    height: int
    meta: GenerationMetaResponse | None


class TryOnResponse(BaseModel):
    """Try-on generation response."""

    image_b64: str
    clothing_composite_b64: str | None
    meta: GenerationMetaResponse | None


class VideoLoopResponse(BaseModel):
    """Video loop generation response."""

    video_b64: str
    first_frame_b64: str
    duration_seconds: float
    width: int
    height: int
    mode: str
    meta: GenerationMetaResponse | None
