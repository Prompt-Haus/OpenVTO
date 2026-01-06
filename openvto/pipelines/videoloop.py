"""Video loop generation pipeline."""

from __future__ import annotations

from openvto.errors import PipelineError, ValidationError
from openvto.prompts import load_prompt
from openvto.providers.base import Provider, VideoGenerationRequest
from openvto.storage.base import Storage
from openvto.types import GenerationMeta, TryOnResult, VideoLoopMode, VideoLoopResult
from openvto.utils.hashing import generate_video_cache_key, short_hash
from openvto.utils.images import get_image_dimensions, load_image_bytes
from openvto.utils.timing import Timer


def generate_videoloop(
    static_image: TryOnResult | bytes | str,
    *,
    provider: Provider,
    storage: Storage | None = None,
    mode: str | VideoLoopMode = VideoLoopMode.TURN_360,
    seconds: float = 4.0,
    prompt_preset: str | None = None,
    prompt_override: str | None = None,
    seed: int | None = None,
) -> VideoLoopResult:
    """Generate an animated video loop from a static try-on image.

    This pipeline:
    1. Extracts source image
    2. Determines prompt preset from mode
    3. Checks cache for existing result
    4. Renders prompt from template
    5. Calls provider to generate video
    6. Caches and returns result

    Args:
        static_image: Try-on result, image bytes, or path.
        provider: Provider instance for video generation.
        storage: Optional storage for caching.
        mode: Animation mode ("360", "idle").
        seconds: Video duration in seconds (4-8).
        prompt_preset: Prompt preset override (auto-selected from mode if None).
        prompt_override: Optional full prompt override.
        seed: Random seed for reproducibility.

    Returns:
        VideoLoopResult with generated video and metadata.

    Raises:
        ValidationError: If inputs are invalid.
        PipelineError: If generation fails.
    """
    timer = Timer().start()

    # Validate duration
    if seconds < 4 or seconds > 8:
        raise ValidationError(f"Duration must be between 4-8 seconds, got {seconds}")

    # Resolve mode enum
    if isinstance(mode, str):
        try:
            mode = VideoLoopMode(mode)
        except ValueError:
            mode = VideoLoopMode.TURN_360

    # Extract source image
    if isinstance(static_image, TryOnResult):
        image_bytes = static_image.image
    else:
        image_bytes = load_image_bytes(static_image)

    # Get image dimensions
    try:
        width, height = get_image_dimensions(image_bytes)
    except Exception:
        width, height = 720, 1280

    # Determine prompt preset from mode
    if prompt_preset is None:
        preset_map = {
            VideoLoopMode.TURN_360: "360_v1",
            VideoLoopMode.IDLE: "idle_v1",
        }
        prompt_preset = preset_map.get(mode, "360_v1")

    # Load prompt config
    prompt_config = load_prompt("videoloop", prompt_preset)
    prompt_version = f"{prompt_config.name}:{prompt_config.version}:{prompt_preset}"

    # Generate cache key
    cache_key = generate_video_cache_key(
        image_bytes,
        mode.value,
        seconds,
        prompt_version,
    )

    # Check cache
    if storage:
        cached_data, cached_entry = storage.get_with_entry(cache_key)
        if cached_data is not None:
            # For video, we also need first/last frames from metadata
            first_frame = image_bytes  # Use input as first frame
            last_frame = image_bytes  # Default to same

            if cached_entry and cached_entry.metadata:
                # Try to get stored frames
                first_key = cached_entry.metadata.get("first_frame_key")
                last_key = cached_entry.metadata.get("last_frame_key")
                if first_key:
                    first_frame = storage.get(first_key) or image_bytes
                if last_key:
                    last_frame = storage.get(last_key) or image_bytes

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

            return VideoLoopResult(
                video=cached_data,
                first_frame=first_frame,
                last_frame=last_frame,
                duration_seconds=seconds,
                width=width,
                height=height,
                mode=mode,
                meta=meta,
            )

    # Build prompt
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = prompt_config.render(subject="the person in the image")

    # Create generation request
    request = VideoGenerationRequest(
        prompt=prompt,
        image=image_bytes,
        duration_seconds=seconds,
        width=width,
        height=height,
        seed=seed,
    )

    # Generate video
    try:
        response = provider.generate_video(request)
    except Exception as e:
        raise PipelineError(f"Video generation failed: {e}", step="videoloop", cause=e)

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
        # Cache video
        storage.put(
            cache_key,
            response.video,
            content_type="video/mp4",
            metadata={
                "model": meta.model,
                "provider": meta.provider,
                "seed": meta.seed,
                "prompt": prompt,
                "mode": mode.value,
                "duration_seconds": seconds,
            },
        )

    return VideoLoopResult(
        video=response.video,
        first_frame=response.first_frame,
        last_frame=response.last_frame,
        duration_seconds=response.duration_seconds,
        width=response.width,
        height=response.height,
        mode=mode,
        meta=meta,
    )
