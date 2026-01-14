"""Utility functions for the API."""

import base64

from app.models.responses import GenerationMetaResponse


def bytes_to_b64(data: bytes) -> str:
    """Convert bytes to base64 string."""
    return base64.b64encode(data).decode("utf-8")


def meta_to_response(meta) -> GenerationMetaResponse | None:
    """Convert GenerationMeta to response model."""
    if meta is None:
        return None
    return GenerationMetaResponse(
        model=meta.model,
        provider=meta.provider,
        latency_ms=meta.latency_ms,
        seed=meta.seed,
    )
