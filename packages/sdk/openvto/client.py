"""Main OpenVTO client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from openvto.errors import ConfigurationError
from openvto.pipelines import generate_avatar, generate_tryon, generate_videoloop
from openvto.providers.base import Provider
from openvto.providers.google import GoogleProvider
from openvto.providers.mock import MockProvider
from openvto.types import ImageModel, PipelineResult, VideoModel
from openvto.utils.timing import Timer

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage

    from openvto.types import (
        AvatarResult,
        ImageInput,
        Outfit,
        TryOnResult,
        VideoLoopResult,
    )

# Return type options
AvatarReturnType = Literal["result", "pil", "bytes"]
TryOnReturnType = Literal["result", "pil", "bytes"]
VideoLoopReturnType = Literal["result", "bytes", "b64"]


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
        image_model: str = ImageModel.NANO_BANANA_PRO.value,
        video_model: str = VideoModel.VEO_31_FAST.value,
        prompt_preset: str = "studio_v1",
    ) -> None:
        """Initialize the OpenVTO client.

        Args:
            provider: Provider to use for generation ("google" or "mock").
            api_key: API key for the provider. If None, reads from environment.
            image_model: Image generation model (default: gemini-2.5-flash-image).
            video_model: Video generation model (default: veo-3.1).
            prompt_preset: Prompt template preset to use.
        """
        self.provider_name = provider
        self.api_key = api_key
        self.image_model = image_model
        self.video_model = video_model
        self.prompt_preset = prompt_preset

        # Initialize provider
        self._provider = self._create_provider()

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

    @property
    def provider(self) -> Provider:
        """Get the current provider instance."""
        return self._provider

    # Overloads for generate_avatar return type
    @overload
    def generate_avatar(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        *,
        background: str = "studio",
        keep_clothes: bool = True,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: None = None,
    ) -> AvatarResult: ...

    @overload
    def generate_avatar(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        *,
        background: str = "studio",
        keep_clothes: bool = True,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: Literal["result"],
    ) -> AvatarResult: ...

    @overload
    def generate_avatar(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        *,
        background: str = "studio",
        keep_clothes: bool = True,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: Literal["pil"],
    ) -> PILImage: ...

    @overload
    def generate_avatar(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        *,
        background: str = "studio",
        keep_clothes: bool = True,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: Literal["bytes"],
    ) -> bytes: ...

    def generate_avatar(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        *,
        background: str = "studio",
        keep_clothes: bool = True,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: AvatarReturnType | None = None,
    ) -> AvatarResult | PILImage | bytes:
        """Generate a studio-quality avatar from selfie and posture images.

        Args:
            selfie: Selfie/face image for identity.
            posture: Full-body posture reference image.
            background: Background style ("studio", "white", "gradient", or "custom").
            keep_clothes: If True, preserve original clothing. If False (default),
                replace with neutral gray bodysuit for clean try-on base.
            prompt: Optional custom prompt override.
            seed: Random seed for reproducibility.
            return_type: How to return the result:
                - None or "result" (default): Return full AvatarResult object
                - "pil": Return as PIL Image
                - "bytes": Return raw image bytes

        Returns:
            AvatarResult, PIL Image, or bytes depending on return_type.
        """
        result = generate_avatar(
            selfie=selfie,
            posture=posture,
            provider=self._provider,
            background=background,
            keep_clothes=keep_clothes,
            prompt_preset=self.prompt_preset,
            prompt_override=prompt,
            seed=seed,
        )

        # Handle return type conversion
        if return_type is None or return_type == "result":
            return result
        elif return_type == "bytes":
            return result.image
        elif return_type == "pil":
            try:
                import io

                from PIL import Image
            except ImportError:
                raise ImportError(
                    "Pillow is required for return_type='pil'. "
                    "Install it with: pip install Pillow"
                ) from None
            return Image.open(io.BytesIO(result.image))
        else:
            raise ValueError(
                f"Invalid return_type '{return_type}'. "
                "Valid options: None, 'result', 'pil', 'bytes'"
            )

    # Overloads for generate_tryon return type
    @overload
    def generate_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        prompt: str | None = None,
        compose: bool = True,
        seed: int | None = None,
        aspect_ratio: str | None = None,
        return_type: None = None,
    ) -> TryOnResult: ...

    @overload
    def generate_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        prompt: str | None = None,
        compose: bool = True,
        seed: int | None = None,
        aspect_ratio: str | None = None,
        return_type: Literal["result"],
    ) -> TryOnResult: ...

    @overload
    def generate_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        prompt: str | None = None,
        compose: bool = True,
        seed: int | None = None,
        aspect_ratio: str | None = None,
        return_type: Literal["pil"],
    ) -> PILImage: ...

    @overload
    def generate_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        prompt: str | None = None,
        compose: bool = True,
        seed: int | None = None,
        aspect_ratio: str | None = None,
        return_type: Literal["bytes"],
    ) -> bytes: ...

    def generate_tryon(
        self,
        avatar: AvatarResult | ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        prompt: str | None = None,
        compose: bool = True,
        seed: int | None = None,
        aspect_ratio: str | None = None,
        return_type: TryOnReturnType | None = None,
    ) -> TryOnResult | PILImage | bytes:
        """Generate virtual try-on with clothing on avatar.

        Args:
            avatar: Avatar result or image to use as base.
            clothes: List of clothing images or an Outfit object.
            prompt: Optional custom prompt override.
            compose: Whether to composite clothing images first.
            seed: Random seed for reproducibility.
            aspect_ratio: Output aspect ratio (e.g., "9:16", "16:9", "1:1", "4:3", "3:4").
                If None, uses avatar dimensions or defaults to "9:16".
            return_type: How to return the result:
                - None or "result" (default): Return full TryOnResult object
                - "pil": Return as PIL Image
                - "bytes": Return raw image bytes

        Returns:
            TryOnResult, PIL Image, or bytes depending on return_type.
        """
        result = generate_tryon(
            avatar=avatar,
            clothes=clothes,
            provider=self._provider,
            prompt_preset=self.prompt_preset,
            prompt_override=prompt,
            compose=compose,
            seed=seed,
            aspect_ratio=aspect_ratio,
        )

        # Handle return type conversion
        if return_type is None or return_type == "result":
            return result
        elif return_type == "bytes":
            return result.image
        elif return_type == "pil":
            try:
                import io

                from PIL import Image
            except ImportError:
                raise ImportError(
                    "Pillow is required for return_type='pil'. "
                    "Install it with: pip install Pillow"
                ) from None
            return Image.open(io.BytesIO(result.image))
        else:
            raise ValueError(
                f"Invalid return_type '{return_type}'. "
                "Valid options: None, 'result', 'pil', 'bytes'"
            )

    # Overloads for generate_videoloop return type
    @overload
    def generate_videoloop(
        self,
        static_image: ImageInput,
        *,
        mode: str = "360",
        seconds: float = 4.0,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: None = None,
    ) -> VideoLoopResult: ...

    @overload
    def generate_videoloop(
        self,
        static_image: ImageInput,
        *,
        mode: str = "360",
        seconds: float = 4.0,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: Literal["result"],
    ) -> VideoLoopResult: ...

    @overload
    def generate_videoloop(
        self,
        static_image: ImageInput,
        *,
        mode: str = "360",
        seconds: float = 4.0,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: Literal["bytes"],
    ) -> bytes: ...

    @overload
    def generate_videoloop(
        self,
        static_image: ImageInput,
        *,
        mode: str = "360",
        seconds: float = 4.0,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: Literal["b64"],
    ) -> str: ...

    def generate_videoloop(
        self,
        static_image: ImageInput,
        *,
        mode: str = "360",
        seconds: float = 4.0,
        prompt: str | None = None,
        seed: int | None = None,
        return_type: VideoLoopReturnType | None = None,
    ) -> VideoLoopResult | bytes | str:
        """Generate an animated video loop from a static try-on image.

        Args:
            static_image: Static image to animate.
            mode: Animation mode ("360" for turn, "idle" for breathing).
            seconds: Video duration in seconds (4-8).
            prompt: Optional custom prompt override.
            seed: Random seed for reproducibility.
            return_type: How to return the result:
                - None or "result" (default): Return full VideoLoopResult object
                - "bytes": Return raw video bytes
                - "b64": Return base64-encoded string (for HTML embedding)

        Returns:
            VideoLoopResult, bytes, or base64 string depending on return_type.
        """
        result = generate_videoloop(
            static_image=static_image,
            provider=self._provider,
            mode=mode,
            seconds=seconds,
            prompt_override=prompt,
            seed=seed,
        )

        # Handle return type conversion
        if return_type is None or return_type == "result":
            return result
        elif return_type == "bytes":
            return result.video
        elif return_type == "b64":
            import base64

            return base64.b64encode(result.video).decode("utf-8")
        else:
            raise ValueError(
                f"Invalid return_type '{return_type}'. "
                "Valid options: None, 'result', 'bytes', 'b64'"
            )

    def pipeline(
        self,
        selfie: ImageInput,
        posture: ImageInput,
        clothes: list[ImageInput] | Outfit,
        *,
        make_video: bool = True,
        background: str = "studio",
        keep_clothes: bool = False,
        seed: int | None = None,
    ) -> PipelineResult:
        """Run the full pipeline: avatar → try-on → video.

        Args:
            selfie: Selfie/face image for identity.
            posture: Full-body posture reference image.
            clothes: Clothing images or Outfit for try-on.
            make_video: Whether to generate video loop.
            background: Background style for avatar.
            keep_clothes: If True, preserve original clothing in avatar.
                If False (default), replace with neutral bodysuit.
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
            keep_clothes=keep_clothes,
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
