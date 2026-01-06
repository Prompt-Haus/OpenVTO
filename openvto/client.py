"""Main OpenVTO client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvto.errors import ConfigurationError
from openvto.pipelines import generate_avatar, generate_tryon, generate_videoloop
from openvto.providers.base import Provider
from openvto.providers.google import GoogleProvider
from openvto.providers.mock import MockProvider
from openvto.storage.base import NullStorage, Storage
from openvto.storage.local import LocalStorage
from openvto.types import ImageModel, PipelineResult, VideoModel
from openvto.utils.timing import Timer

if TYPE_CHECKING:
    from openvto.types import (
        AvatarResult,
        ImageInput,
        Outfit,
        TryOnResult,
        VideoLoopResult,
    )


class OpenVTO:
    """Main client for OpenVTO virtual try-on generation.

    Example:
        >>> from openvto import OpenVTO
        >>> vto = OpenVTO(provider="mock")
        >>> avatar = vto.generate_avatar(selfie="selfie.jpg", posture="fullbody.jpg")
        >>> tryon = vto.generate_tryon(avatar, clothes=["shirt.jpg", "pants.jpg"])
        >>> video = vto.generate_videoloop(tryon.image)
    """

    def __init__(
        self,
        *,
        provider: str = "google",
        api_key: str | None = None,
        image_model: str = ImageModel.NANO_BANANA.value,
        video_model: str = VideoModel.VEO_31.value,
        cache_enabled: bool = True,
        cache_dir: str | None = None,
        prompt_preset: str = "studio_v1",
    ) -> None:
        """Initialize the OpenVTO client.

        Args:
            provider: Provider to use for generation ("google" or "mock").
            api_key: API key for the provider. If None, reads from environment.
            image_model: Image generation model (default: gemini-2.5-flash-image).
            video_model: Video generation model (default: veo-3.1).
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

        # Initialize provider
        self._provider = self._create_provider()

        # Initialize storage
        self._storage = self._create_storage()

    def _create_provider(self) -> Provider:
        """Create the appropriate provider instance."""
        if self.provider_name == "google":
            return GoogleProvider(
                api_key=self.api_key,
                image_model=self.image_model,
                video_model=self.video_model,
            )
        elif self.provider_name == "mock":
            return MockProvider()
        else:
            raise ConfigurationError(
                f"Unknown provider: {self.provider_name}. "
                "Supported providers: 'google', 'mock'"
            )

    def _create_storage(self) -> Storage:
        """Create the storage backend."""
        if not self.cache_enabled:
            return NullStorage()
        return LocalStorage(cache_dir=self.cache_dir)

    @property
    def provider(self) -> Provider:
        """Get the current provider instance."""
        return self._provider

    @property
    def storage(self) -> Storage:
        """Get the current storage instance."""
        return self._storage

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
        return generate_avatar(
            selfie=selfie,
            posture=posture,
            provider=self._provider,
            storage=self._storage if self.cache_enabled else None,
            background=background,
            prompt_preset=self.prompt_preset,
            prompt_override=prompt,
            seed=seed,
        )

    def generate_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        prompt: str | None = None,
        compose: bool = True,
        seed: int | None = None,
    ) -> TryOnResult:
        """Generate virtual try-on with clothing on avatar.

        Args:
            avatar: Avatar result or image to use as base.
            clothes: List of clothing images or an Outfit object.
            prompt: Optional custom prompt override.
            compose: Whether to composite clothing images first.
            seed: Random seed for reproducibility.

        Returns:
            TryOnResult with generated try-on and metadata.
        """
        return generate_tryon(
            avatar=avatar,
            clothes=clothes,
            provider=self._provider,
            storage=self._storage if self.cache_enabled else None,
            prompt_preset=self.prompt_preset,
            prompt_override=prompt,
            compose=compose,
            seed=seed,
        )

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
        return generate_videoloop(
            static_image=static_image,
            provider=self._provider,
            storage=self._storage if self.cache_enabled else None,
            mode=mode,
            seconds=seconds,
            prompt_override=prompt,
            seed=seed,
        )

    def pipeline(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        make_video: bool = True,
        background: str = "studio",
        seed: int | None = None,
    ) -> PipelineResult:
        """Run the full pipeline: avatar → try-on → video.

        Args:
            selfie: Selfie/face image for identity.
            posture: Full-body posture reference image.
            clothes: Clothing images or Outfit for try-on.
            make_video: Whether to generate video loop.
            background: Background style for avatar.
            seed: Random seed for reproducibility.

        Returns:
            PipelineResult with all generated assets.
        """
        timer = Timer().start()

        # Generate avatar
        avatar_result = self.generate_avatar(
            selfie=selfie,
            posture=posture,
            background=background,
            seed=seed,
        )

        # Generate try-on
        tryon_result = self.generate_tryon(
            avatar=avatar_result,
            clothes=clothes,
            seed=seed,
        )

        # Generate video (optional)
        video_result = None
        if make_video:
            video_result = self.generate_videoloop(
                static_image=tryon_result,
                seed=seed,
            )

        total_ms = timer.stop()

        return PipelineResult(
            avatar=avatar_result,
            tryon=tryon_result,
            video=video_result,
            total_latency_ms=total_ms,
        )
