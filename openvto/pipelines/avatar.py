"""Avatar generation pipeline."""

from __future__ import annotations

from openvto.errors import PipelineError, ValidationError
from openvto.prompts import load_prompt
from openvto.providers.base import ImageGenerationRequest, Provider
from openvto.storage.base import Storage
from openvto.types import Avatar, AvatarResult, Background, GenerationMeta
from openvto.utils.hashing import generate_avatar_cache_key, short_hash
from openvto.utils.images import load_image_bytes, normalize_for_generation
from openvto.utils.timing import Timer


def generate_avatar(
    selfie: str | bytes,
    posture: str | bytes,
    *,
    provider: Provider,
    storage: Storage | None = None,
    background: str | Background = Background.STUDIO,
    keep_clothes: bool = False,
    prompt_preset: str = "studio_v1",
    prompt_override: str | None = None,
    seed: int | None = None,
    width: int = 720,
    height: int = 1280,
) -> AvatarResult:
    """Generate a studio-quality avatar from selfie and posture images.

    This pipeline:
    1. Loads and normalizes input images
    2. Checks cache for existing result
    3. Renders prompt from template
    4. Calls provider to generate avatar
    5. Caches and returns result

    Args:
        selfie: Selfie/face image (path or bytes).
        posture: Full-body posture reference (path or bytes).
        provider: Provider instance for image generation.
        storage: Optional storage for caching.
        background: Background style to use.
        keep_clothes: If True, preserve original clothing. If False (default),
            replace with neutral gray bodysuit for clean try-on base.
        prompt_preset: Prompt preset name.
        prompt_override: Optional full prompt override.
        seed: Random seed for reproducibility.
        width: Output width in pixels.
        height: Output height in pixels.

    Returns:
        AvatarResult with generated avatar and metadata.

    Raises:
        ValidationError: If inputs are invalid.
        PipelineError: If generation fails.
    """
    timer = Timer().start()

    # Resolve background enum
    if isinstance(background, str):
        try:
            background = Background(background)
        except ValueError:
            background = Background.STUDIO

    # Load and normalize images
    try:
        selfie_bytes = load_image_bytes(selfie)
        posture_bytes = load_image_bytes(posture)
    except Exception as e:
        raise ValidationError(f"Failed to load input images: {e}")

    # Normalize to target dimensions
    selfie_normalized = normalize_for_generation(
        selfie_bytes, target_width=width, target_height=height
    )
    posture_normalized = normalize_for_generation(
        posture_bytes, target_width=width, target_height=height
    )

    # Load prompt config
    prompt_config = load_prompt("avatar", prompt_preset)
    prompt_version = f"{prompt_config.name}:{prompt_config.version}:{prompt_preset}"

    # Generate cache key (include keep_clothes in key)
    cache_key = generate_avatar_cache_key(
        selfie_normalized,
        posture_normalized,
        background.value,
        f"{prompt_version}:keep_clothes={keep_clothes}",
    )

    # Check cache
    if storage:
        cached_data, cached_entry = storage.get_with_entry(cache_key)
        if cached_data is not None:
            # Cache hit
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
            avatar = Avatar(
                image=cached_data,
                width=width,
                height=height,
                background=background,
                meta=meta,
            )
            return AvatarResult(
                avatar=avatar,
                selfie_hash=short_hash(selfie_bytes),
                posture_hash=short_hash(posture_bytes),
            )

    # Build prompt
    if prompt_override:
        prompt = prompt_override
    else:
        # Build clothing instruction based on keep_clothes setting
        if keep_clothes:
            clothing_instruction = (
                "Keep the person wearing exactly the same clothing as in the reference image. "
                "Preserve all clothing details, colors, and styling exactly as shown."
            )
        else:
            clothing_instruction = (
                "Replace the person's clothing with a form-fitting neutral gray bodysuit/onesie. "
                "The bodysuit should be plain, simple, and body-tight to serve as a clean base "
                "for virtual try-on. Remove all original clothing and accessories."
            )

        # Render base prompt and append clothing instruction
        base_prompt = prompt_config.render(
            subject="the person from the reference image"
        )
        prompt = f"{base_prompt}. {clothing_instruction}"

    # Create generation request
    request = ImageGenerationRequest(
        prompt=prompt,
        width=width,
        height=height,
        seed=seed,
        reference_image=posture_normalized,  # Use posture as reference for body
    )

    # Generate avatar
    try:
        response = provider.edit_image(request)
    except Exception as e:
        raise PipelineError(f"Avatar generation failed: {e}", step="avatar", cause=e)

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
                "background": background.value,
                "keep_clothes": keep_clothes,
            },
        )

    # Build result
    avatar = Avatar(
        image=response.image,
        width=response.width,
        height=response.height,
        background=background,
        meta=meta,
    )

    return AvatarResult(
        avatar=avatar,
        selfie_hash=short_hash(selfie_bytes),
        posture_hash=short_hash(posture_bytes),
    )
