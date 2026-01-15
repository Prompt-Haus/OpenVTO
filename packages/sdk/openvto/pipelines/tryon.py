"""Try-on generation pipeline."""

from __future__ import annotations

import json

from openvto.errors import PipelineError, ValidationError
from openvto.pipelines.composer import compose_clothing
from openvto.prompts import load_prompt
from openvto.providers.base import ImageGenerationRequest, Provider
from openvto.types import (
    AvatarResult,
    ClothingItem,
    GenerationMeta,
    Outfit,
    TryOnResult,
    TryOnVariant,
)
from openvto.utils.hashing import short_hash
from openvto.utils.images import load_image_bytes
from openvto.utils.timing import Timer


# Aspect ratio to dimensions mapping (using 1K resolution)
ASPECT_RATIO_DIMENSIONS: dict[str, tuple[int, int]] = {
    "9:16": (720, 1280),
    "16:9": (1280, 720),
    "1:1": (1024, 1024),
    "4:3": (1024, 768),
    "3:4": (768, 1024),
}


def _format_styling(spec: dict | list | str | None) -> str | None:
    """Format styling specification as a prompt appendix block.

    Args:
        spec: Styling specification. Can be:
            - None: Returns None (no appendix)
            - dict/list: Serialized to JSON with indentation
            - str: Used as-is (JSON string or plain text)

    Returns:
        Formatted appendix block with [clothing_styling_guidelines] tags,
        or None if spec is None.
    """
    if spec is None:
        return None

    if isinstance(spec, (dict, list)):
        content = json.dumps(spec, indent=2)
    else:
        content = str(spec)

    return f"\n\n[clothing_styling_guidelines]\n{content}\n[/clothing_styling_guidelines]\n"


def generate_tryon(
    avatar: AvatarResult | bytes | str,
    clothes: list[ClothingItem] | Outfit | list[str] | list[bytes],
    *,
    provider: Provider,
    prompt_preset: str = "studio_v1",
    prompt_override: str | None = None,
    compose: bool = True,
    seed: int | None = None,
    aspect_ratio: str | None = None,
    styling: dict | str | None = None,
) -> TryOnResult:
    """Generate virtual try-on with clothing on avatar.

    This pipeline:
    1. Extracts avatar image
    2. Composes clothing items (if multiple)
    3. Renders prompt from template
    4. Calls provider to generate try-on
    5. Returns result

    Args:
        avatar: Avatar result, image bytes, or path.
        clothes: Clothing items, Outfit, or list of image paths/bytes.
        provider: Provider instance for image generation.
        prompt_preset: Prompt preset name.
        prompt_override: Optional full prompt override.
        compose: Whether to composite multiple clothing items.
        seed: Random seed for reproducibility.
        aspect_ratio: Output aspect ratio (e.g., "9:16", "16:9", "1:1", "4:3", "3:4").
            If None, uses avatar dimensions or defaults to "9:16".
        styling: Optional clothing fit/proportions/sizing context appended to prompt.
            Can be a dict (serialized to JSON), a JSON string, or plain text.
            Use to provide additional guidance on how clothes should fit the avatar
            (e.g., {"coat": "knee-length", "pants": "slim fit"}).

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

    # Override dimensions if aspect_ratio is provided
    if aspect_ratio is not None:
        if aspect_ratio not in ASPECT_RATIO_DIMENSIONS:
            raise ValidationError(
                f"Invalid aspect_ratio '{aspect_ratio}'. "
                f"Supported values: {', '.join(ASPECT_RATIO_DIMENSIONS.keys())}"
            )
        width, height = ASPECT_RATIO_DIMENSIONS[aspect_ratio]

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

    # Build prompt
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = prompt_config.render(
            subject="the person",
            clothing_description=clothing_description,
        )

    # Append styling guidelines if provided
    styling_appendix = _format_styling(styling)
    if styling_appendix:
        prompt += styling_appendix

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
        prompt=prompt,
        prompt_version=prompt_version,
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
