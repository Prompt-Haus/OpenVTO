"""Main OpenVTO client."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openvto.types import (
        AvatarResult,
        BatchTryOnResult,
        ImageInput,
        Outfit,
        PipelineResult,
        TryOnResult,
        VideoLoopResult,
    )


class OpenVTO:
    """Main client for OpenVTO virtual try-on generation.

    Example:
        >>> from openvto import OpenVTO
        >>> vto = OpenVTO()
        >>> avatar = vto.generate_avatar(selfie="selfie.jpg", posture="fullbody.jpg")
        >>> tryon = vto.generate_tryon(avatar, clothes=["shirt.jpg", "pants.jpg"])
        >>> video = vto.generate_videoloop(tryon.image)
    """

    def __init__(
        self,
        *,
        provider: str = "google",
        api_key: str | None = None,
        image_model: str = "imagen",
        video_model: str = "veo",
        cache_enabled: bool = True,
        cache_dir: str | None = None,
        prompt_preset: str = "studio_v1",
    ) -> None:
        """Initialize the OpenVTO client.

        Args:
            provider: Provider to use for generation ("google" or "mock").
            api_key: API key for the provider. If None, reads from environment.
            image_model: Image generation model ("imagen" or "imagen-pro").
            video_model: Video generation model ("veo" or "veo-fast").
            cache_enabled: Whether to enable caching of generated assets.
            cache_dir: Directory for cache storage. Defaults to ~/.openvto/cache.
            prompt_preset: Prompt template preset to use.
        """
        self.provider_name = provider
        self.api_key = api_key
        self.image_model = image_model
        self.video_model = video_model
        self.cache_enabled = cache_enabled
        self.cache_dir = cache_dir
        self.prompt_preset = prompt_preset

        # TODO: Initialize provider, storage, and prompt loader in Phase 2+

    def generate_avatar(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        *,
        background: str = "studio",
        prompt: str | None = None,
        seed: int | None = None,
    ) -> AvatarResult:
        """Generate a studio-quality avatar from selfie and posture images.

        Args:
            selfie: Selfie/face image for identity.
            posture: Full-body posture reference image.
            background: Background style ("studio", "white", "gradient", or "custom").
            prompt: Optional custom prompt override.
            seed: Random seed for reproducibility.

        Returns:
            AvatarResult with the generated avatar and metadata.
        """
        raise NotImplementedError("Avatar generation will be implemented in Phase 6")

    def generate_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        variants: int = 1,
        prompt: str | None = None,
        compose: bool = True,
    ) -> TryOnResult:
        """Generate virtual try-on with clothing on avatar.

        Args:
            avatar: Avatar result or image to use as base.
            clothes: List of clothing images or an Outfit object.
            variants: Number of variants to generate (1-4).
            prompt: Optional custom prompt override.
            compose: Whether to composite clothing images first.

        Returns:
            TryOnResult with generated try-on variants and metadata.
        """
        raise NotImplementedError("Try-on generation will be implemented in Phase 6")

    def generate_videoloop(
        self,
        static_image: ImageInput,
        *,
        mode: str = "360",
        seconds: float = 4.0,
        prompt: str | None = None,
        seed: int | None = None,
    ) -> VideoLoopResult:
        """Generate an animated video loop from a static try-on image.

        Args:
            static_image: Static image to animate.
            mode: Animation mode ("360" for turn, "idle" for breathing).
            seconds: Video duration in seconds (4-8).
            prompt: Optional custom prompt override.
            seed: Random seed for reproducibility.

        Returns:
            VideoLoopResult with the generated video and metadata.
        """
        raise NotImplementedError(
            "Video loop generation will be implemented in Phase 6"
        )

    def pipeline(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        variants: int = 1,
        make_video: bool = True,
    ) -> PipelineResult:
        """Run the full pipeline: avatar → try-on → video.

        Args:
            selfie: Selfie/face image for identity.
            posture: Full-body posture reference image.
            clothes: Clothing images or Outfit for try-on.
            variants: Number of try-on variants to generate.
            make_video: Whether to generate video loop.

        Returns:
            PipelineResult with all generated assets.
        """
        raise NotImplementedError("Full pipeline will be implemented in Phase 6")

    def batch_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        outfits: list[Outfit],
        *,
        variants: int = 1,
    ) -> BatchTryOnResult:
        """Generate try-ons for multiple outfits in batch.

        Args:
            avatar: Avatar result or image to use as base.
            outfits: List of outfits to try on.
            variants: Number of variants per outfit.

        Returns:
            BatchTryOnResult with results for each outfit.
        """
        raise NotImplementedError("Batch try-on will be implemented in Phase 6")
