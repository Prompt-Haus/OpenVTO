"""Try-on generation pipeline."""

from __future__ import annotations

from openvto.errors import PipelineError, ValidationError
from openvto.pipelines.composer import compose_clothing
from openvto.prompts import load_prompt
from openvto.providers.base import ImageGenerationRequest, Provider
from openvto.storage.base import Storage
from openvto.types import (
    AvatarResult,
    ClothingItem,
    GenerationMeta,
    Outfit,
    TryOnResult,
    TryOnVariant,
)
from openvto.utils.hashing import generate_tryon_cache_key, short_hash
from openvto.utils.images import load_image_bytes
from openvto.utils.timing import Timer


def generate_tryon(
    avatar: AvatarResult | bytes | str,
    clothes: list[ClothingItem] | Outfit | list[str] | list[bytes],
    *,
    provider: Provider,
    storage: Storage | None = None,
    prompt_preset: str = "studio_v1",
    prompt_override: str | None = None,
    compose: bool = True,
    seed: int | None = None,
) -> TryOnResult:
    """Generate virtual try-on with clothing on avatar.

    This pipeline:
    1. Extracts avatar image
    2. Composes clothing items (if multiple)
    3. Checks cache for existing result
    4. Renders prompt from template
    5. Calls provider to generate try-on
    6. Caches and returns result

    Args:
        avatar: Avatar result, image bytes, or path.
        clothes: Clothing items, Outfit, or list of image paths/bytes.
        provider: Provider instance for image generation.
        storage: Optional storage for caching.
        prompt_preset: Prompt preset name.
        prompt_override: Optional full prompt override.
        compose: Whether to composite multiple clothing items.
        seed: Random seed for reproducibility.

    Returns:
        TryOnResult with generated try-on and metadata.

    Raises:
        ValidationError: If inputs are invalid.
        PipelineError: If generation fails.
    """
    timer = Timer().start()

    # Extract avatar image
    if isinstance(avatar, AvatarResult):
        avatar_bytes = avatar.image
        width = avatar.avatar.width
        height = avatar.avatar.height
    else:
        avatar_bytes = load_image_bytes(avatar)
        # Default dimensions
        width = 720
        height = 1280

    # Normalize clothing input
    clothing_items = _normalize_clothing_input(clothes)

    # Compose clothing if needed
    if compose and len(clothing_items) > 1:
        composite = compose_clothing(clothing_items)
        clothing_bytes = composite.image
        clothing_description = composite.description
    elif len(clothing_items) == 1:
        clothing_bytes = load_image_bytes(clothing_items[0].image)
        clothing_description = _build_single_description(clothing_items[0])
    else:
        raise ValidationError("No clothing items provided")

    # Load prompt config
    prompt_config = load_prompt("tryon", prompt_preset)
    prompt_version = f"{prompt_config.name}:{prompt_config.version}:{prompt_preset}"

    # Generate cache key
    cache_key = generate_tryon_cache_key(
        avatar_bytes,
        clothing_bytes,
        prompt_version,
    )

    # Check cache
    if storage:
        cached_data, cached_entry = storage.get_with_entry(cache_key)
        if cached_data is not None:
            meta = GenerationMeta(
                model=(
                    cached_entry.metadata.get("model", "unknown")
                    if cached_entry.metadata
                    else "unknown"
                ),
                provider=(
                    cached_entry.metadata.get("provider", "cache")
                    if cached_entry.metadata
                    else "cache"
                ),
                seed=(
                    cached_entry.metadata.get("seed") if cached_entry.metadata else None
                ),
                latency_ms=timer.elapsed_ms,
                cache_hit=True,
                cache_key=cache_key,
                prompt=(
                    cached_entry.metadata.get("prompt")
                    if cached_entry.metadata
                    else None
                ),
                prompt_version=prompt_version,
            )
            variant = TryOnVariant(image=cached_data, meta=meta)
            return TryOnResult(
                try_on=variant,
                avatar_hash=short_hash(avatar_bytes),
                clothing_hash=short_hash(clothing_bytes),
                clothing_composite=clothing_bytes,
            )

    # Build prompt
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = prompt_config.render(
            subject="the person",
            clothing_description=clothing_description,
        )

    # Create generation request
    request = ImageGenerationRequest(
        prompt=prompt,
        width=width,
        height=height,
        seed=seed,
        reference_image=avatar_bytes,
        clothing_image=clothing_bytes,
    )

    # Generate try-on
    try:
        response = provider.edit_image(request)
    except Exception as e:
        raise PipelineError(f"Try-on generation failed: {e}", step="tryon", cause=e)

    # Build metadata
    meta = GenerationMeta(
        model=response.model or "unknown",
        provider=provider.name,
        seed=response.seed,
        latency_ms=response.latency_ms,
        cache_hit=False,
        cache_key=cache_key,
        prompt=prompt,
        prompt_version=prompt_version,
    )

    # Cache result
    if storage:
        storage.put(
            cache_key,
            response.image,
            content_type="image/png",
            metadata={
                "model": meta.model,
                "provider": meta.provider,
                "seed": meta.seed,
                "prompt": prompt,
                "clothing_description": clothing_description,
            },
        )

    # Build result
    variant = TryOnVariant(image=response.image, meta=meta)

    return TryOnResult(
        try_on=variant,
        avatar_hash=short_hash(avatar_bytes),
        clothing_hash=short_hash(clothing_bytes),
        clothing_composite=clothing_bytes,
    )


def _normalize_clothing_input(
    clothes: list[ClothingItem] | Outfit | list[str] | list[bytes],
) -> list[ClothingItem]:
    """Normalize various clothing input formats to list of ClothingItem."""
    if isinstance(clothes, Outfit):
        return clothes.items

    if not clothes:
        return []

    # Check first item type
    first = clothes[0]
    if isinstance(first, ClothingItem):
        return clothes  # type: ignore

    # Convert raw images to ClothingItems
    items = []
    for i, item in enumerate(clothes):
        items.append(
            ClothingItem(
                id=f"item_{i}",
                image=item,  # type: ignore
            )
        )
    return items


def _build_single_description(item: ClothingItem) -> str:
    """Build description for a single clothing item."""
    parts = []
    if item.name:
        parts.append(item.name)
    if item.description:
        parts.append(item.description)
    if item.styling:
        parts.append(item.styling)

    if parts:
        return " ".join(parts)
    return "the clothing item"
