"""Google provider for image and video generation (Gemini + Veo)."""

from __future__ import annotations

import os
import time
from typing import Any

from openvto.errors import (
    ModelNotFoundError,
    ProviderAuthError,
    ProviderError,
    ProviderQuotaError,
    ProviderRateLimitError,
    ValidationError,
)
from openvto.providers.base import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    Provider,
    VideoGenerationRequest,
    VideoGenerationResponse,
)
from openvto.types import ImageModel, VideoModel


class GoogleProvider(Provider):
    """Google provider using Gemini for images and Veo for video.

    Supported models:
    - Image: gemini-2.5-flash-image (NanoBanana), gemini-3-pro-image-preview (NanoBanana Pro)
    - Video: veo-3.1, veo-3.1-fast

    Environment variables:
    - GOOGLE_API_KEY: API key for Google AI services
    """

    DEFAULT_IMAGE_MODEL = ImageModel.NANO_BANANA.value
    DEFAULT_VIDEO_MODEL = VideoModel.VEO_31.value

    def __init__(
        self,
        api_key: str | None = None,
        image_model: str = DEFAULT_IMAGE_MODEL,
        video_model: str = DEFAULT_VIDEO_MODEL,
    ) -> None:
        """Initialize Google provider.

        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
            image_model: Image generation model to use.
            video_model: Video generation model to use.

        Raises:
            ProviderAuthError: If no API key is provided or found.
        """
        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self._image_model = image_model
        self._video_model = video_model
        self._client: Any = None

    @property
    def name(self) -> str:
        return "google"

    def _ensure_client(self) -> Any:
        """Lazily initialize the Google AI client."""
        if self._client is None:
            if not self._api_key:
                raise ProviderAuthError(
                    "Google API key not found. Set GOOGLE_API_KEY environment variable "
                    "or pass api_key to the provider.",
                    provider=self.name,
                )

            try:
                from google import genai

                self._client = genai.Client(api_key=self._api_key)
            except ImportError:
                raise ProviderError(
                    "google-genai package not installed. "
                    "Install with: pip install google-genai",
                    provider=self.name,
                )

        return self._client

    def _handle_api_error(self, error: Exception) -> None:
        """Convert Google API errors to OpenVTO errors."""
        error_str = str(error).lower()

        if (
            "401" in error_str
            or "unauthorized" in error_str
            or "invalid api key" in error_str
        ):
            raise ProviderAuthError(
                f"Google API authentication failed: {error}",
                provider=self.name,
                status_code=401,
            )
        elif "429" in error_str or "rate limit" in error_str or "quota" in error_str:
            if "quota" in error_str:
                raise ProviderQuotaError(
                    f"Google API quota exceeded: {error}",
                    provider=self.name,
                    status_code=429,
                )
            raise ProviderRateLimitError(
                f"Google API rate limit exceeded: {error}",
                provider=self.name,
                status_code=429,
            )
        elif "404" in error_str or "not found" in error_str:
            raise ModelNotFoundError(
                f"Google API model not found: {error}",
                provider=self.name,
                status_code=404,
            )
        else:
            raise ProviderError(
                f"Google API error: {error}",
                provider=self.name,
            )

    def generate_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """Generate an image using Gemini image generation."""
        client = self._ensure_client()
        start = time.perf_counter()

        try:
            # TODO: Implement actual Gemini image generation API call
            # This is a skeleton - actual implementation depends on the API
            response = client.models.generate_images(
                model=self._image_model,
                prompt=request.prompt,
                config={
                    "number_of_images": 1,
                    "aspect_ratio": f"{request.width}:{request.height}",
                },
            )

            # Extract image from response
            image_data = response.generated_images[0].image.image_bytes
            latency = (time.perf_counter() - start) * 1000

            return ImageGenerationResponse(
                image=image_data,
                width=request.width,
                height=request.height,
                seed=request.seed,
                model=self._image_model,
                latency_ms=latency,
            )

        except Exception as e:
            self._handle_api_error(e)
            raise  # Should not reach here

    def edit_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Edit an image using Gemini image editing."""
        if request.reference_image is None:
            raise ValidationError("reference_image is required for edit_image")

        client = self._ensure_client()
        start = time.perf_counter()

        try:
            from google.genai import types

            # TODO: Implement actual Gemini image editing API call
            response = client.models.generate_images(
                model=self._image_model,
                prompt=request.prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    edit_config=types.EditImageConfig(
                        edit_mode="EDIT_MODE_INPAINT_INSERTION",
                    ),
                ),
                image=types.Image(image_bytes=request.reference_image),
            )

            image_data = response.generated_images[0].image.image_bytes
            latency = (time.perf_counter() - start) * 1000

            return ImageGenerationResponse(
                image=image_data,
                width=request.width,
                height=request.height,
                seed=request.seed,
                model=self._image_model,
                latency_ms=latency,
            )

        except Exception as e:
            self._handle_api_error(e)
            raise

    def generate_video(
        self, request: VideoGenerationRequest
    ) -> VideoGenerationResponse:
        """Generate a video using Veo."""
        client = self._ensure_client()
        start = time.perf_counter()

        try:
            from google.genai import types

            # TODO: Implement actual Veo video generation API call
            response = client.models.generate_videos(
                model=self._video_model,
                prompt=request.prompt,
                image=types.Image(image_bytes=request.image),
                config=types.GenerateVideosConfig(
                    aspect_ratio=f"{request.width}:{request.height}",
                    duration_seconds=int(request.duration_seconds),
                ),
            )

            # Poll for completion (video generation is async)
            while not response.done:
                time.sleep(5)
                response = client.operations.get(response)

            video_data = response.generated_videos[0].video.video_bytes
            latency = (time.perf_counter() - start) * 1000

            # Extract frames (implementation depends on actual API response)
            first_frame = request.image  # Use input image as first frame
            last_frame = first_frame  # TODO: Extract actual last frame

            return VideoGenerationResponse(
                video=video_data,
                first_frame=first_frame,
                last_frame=last_frame,
                duration_seconds=request.duration_seconds,
                width=request.width,
                height=request.height,
                seed=request.seed,
                model=self._video_model,
                latency_ms=latency,
            )

        except Exception as e:
            self._handle_api_error(e)
            raise

    def validate_api_key(self) -> bool:
        """Validate that the Google API key is configured."""
        try:
            self._ensure_client()
            return True
        except ProviderAuthError:
            return False
