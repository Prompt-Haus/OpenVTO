"""Base provider interface for image and video generation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class ImageGenerationRequest:
    """Request for image generation.

    Attributes:
        prompt: Text prompt for generation.
        width: Output image width in pixels.
        height: Output image height in pixels.
        seed: Random seed for reproducibility.
        reference_image: Optional reference image bytes for image-to-image.
        clothing_image: Optional clothing image bytes for try-on.
        mask_image: Optional mask image bytes for inpainting.
    """

    prompt: str
    width: int = 1024
    height: int = 1792  # 9:16 aspect ratio
    seed: int | None = None
    reference_image: bytes | None = None
    clothing_image: bytes | None = None
    mask_image: bytes | None = None


@dataclass
class ImageGenerationResponse:
    """Response from image generation.

    Attributes:
        image: Generated image bytes.
        width: Image width in pixels.
        height: Image height in pixels.
        seed: Seed used for generation.
        model: Model used for generation.
        latency_ms: Generation time in milliseconds.
    """

    image: bytes
    width: int
    height: int
    seed: int | None = None
    model: str | None = None
    latency_ms: float | None = None


@dataclass
class VideoGenerationRequest:
    """Request for video generation.

    Attributes:
        prompt: Text prompt for video generation.
        image: First frame / reference image bytes.
        duration_seconds: Video duration in seconds.
        width: Output video width in pixels.
        height: Output video height in pixels.
        seed: Random seed for reproducibility.
    """

    prompt: str
    image: bytes
    duration_seconds: float = 4.0
    width: int = 1024
    height: int = 1792
    seed: int | None = None


@dataclass
class VideoGenerationResponse:
    """Response from video generation.

    Attributes:
        video: Generated video bytes (MP4).
        first_frame: First frame of the video (bytes).
        last_frame: Last frame of the video (bytes).
        duration_seconds: Actual video duration.
        width: Video width in pixels.
        height: Video height in pixels.
        seed: Seed used for generation.
        model: Model used for generation.
        latency_ms: Generation time in milliseconds.
    """

    video: bytes
    first_frame: bytes
    last_frame: bytes
    duration_seconds: float
    width: int
    height: int
    seed: int | None = None
    model: str | None = None
    latency_ms: float | None = None


class Provider(ABC):
    """Abstract base class for generation providers.

    Providers implement the actual API calls to image/video generation services.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        ...

    @abstractmethod
    def generate_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """Generate an image from a prompt.

        Args:
            request: Image generation request parameters.

        Returns:
            ImageGenerationResponse with generated image.

        Raises:
            ProviderError: If generation fails.
        """
        ...

    @abstractmethod
    def edit_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Edit an image using a reference and prompt.

        Args:
            request: Image generation request with reference_image set.

        Returns:
            ImageGenerationResponse with edited image.

        Raises:
            ProviderError: If editing fails.
            ValidationError: If reference_image is not provided.
        """
        ...

    @abstractmethod
    def generate_video(
        self, request: VideoGenerationRequest
    ) -> VideoGenerationResponse:
        """Generate a video from an image and prompt.

        Args:
            request: Video generation request parameters.

        Returns:
            VideoGenerationResponse with generated video.

        Raises:
            ProviderError: If generation fails.
        """
        ...

    def validate_api_key(self) -> bool:
        """Validate that the API key is configured and valid.

        Returns:
            True if valid, False otherwise.
        """
        return True  # Override in implementations that require keys
