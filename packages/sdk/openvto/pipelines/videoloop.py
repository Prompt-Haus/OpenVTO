"""Video loop generation pipeline."""

from __future__ import annotations

from openvto.errors import PipelineError, ValidationError
from openvto.prompts import load_prompt
from openvto.providers.base import Provider, VideoGenerationRequest
from openvto.types import GenerationMeta, TryOnResult, VideoLoopMode, VideoLoopResult
from openvto.utils.images import get_image_dimensions, load_image_bytes


def generate_videoloop(
    static_image: TryOnResult | bytes | str,
    *,
    provider: Provider,
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
    3. Renders prompt from template
    4. Calls provider to generate video
    5. Returns result

    Args:
        static_image: Try-on result, image bytes, or path.
        provider: Provider instance for video generation.
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
        prompt=prompt,
        prompt_version=prompt_version,
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
