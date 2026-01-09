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

    Supports two authentication modes:

    1. Google AI Studio (default):
       - Set GOOGLE_API_KEY environment variable

    2. Vertex AI (enterprise):
       - Set GOOGLE_GENAI_USE_VERTEXAI=true
       - Set GOOGLE_CLOUD_PROJECT to your GCP project ID
       - Set GOOGLE_CLOUD_LOCATION (optional, defaults to us-central1)
       - Ensure proper GCP authentication (gcloud auth, service account, etc.)
    """

    DEFAULT_IMAGE_MODEL = ImageModel.NANO_BANANA_PRO.value
    DEFAULT_VIDEO_MODEL = VideoModel.VEO_31_FAST.value

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
        """Lazily initialize the Google AI client.

        Supports two modes:
        - Google AI Studio: Uses GOOGLE_API_KEY
        - Vertex AI: Uses GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION,
          and GOOGLE_GENAI_USE_VERTEXAI=true
        """
        if self._client is None:
            try:
                from google import genai
            except ImportError:
                raise ProviderError(
                    "google-genai package not installed. "
                    "Install with: pip install google-genai",
                    provider=self.name,
                )

            # Check if Vertex AI mode is requested
            use_vertexai = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in (
                "true",
                "1",
                "yes",
            )

            if use_vertexai:
                # Vertex AI mode - uses GCP project and location
                project = os.environ.get("GOOGLE_CLOUD_PROJECT")
                location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

                if not project:
                    raise ProviderAuthError(
                        "GOOGLE_CLOUD_PROJECT environment variable is required when "
                        "using Vertex AI mode (GOOGLE_GENAI_USE_VERTEXAI=true).",
                        provider=self.name,
                    )

                self._client = genai.Client(
                    vertexai=True,
                    project=project,
                    location=location,
                )
            else:
                # Google AI Studio mode - uses API key
                if not self._api_key:
                    raise ProviderAuthError(
                        "Google API key not found. Set GOOGLE_API_KEY environment variable "
                        "or pass api_key to the provider.",
                        provider=self.name,
                    )

                self._client = genai.Client(api_key=self._api_key)

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

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """Convert dimensions to aspect ratio string."""
        # Common aspect ratios
        ratio = width / height
        if abs(ratio - 9 / 16) < 0.01:
            return "9:16"
        elif abs(ratio - 16 / 9) < 0.01:
            return "16:9"
        elif abs(ratio - 1.0) < 0.01:
            return "1:1"
        elif abs(ratio - 4 / 3) < 0.01:
            return "4:3"
        elif abs(ratio - 3 / 4) < 0.01:
            return "3:4"
        else:
            return "9:16"  # Default for portrait/fashion

    def _extract_image_from_response(self, response: Any) -> bytes:
        """Extract image bytes from Gemini response."""
        # Response contains parts, find the image part
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                return part.inline_data.data
        raise ProviderError("No image found in response", provider=self.name)

    def generate_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """Generate an image using Gemini generate_content with IMAGE modality."""
        client = self._ensure_client()
        start = time.perf_counter()

        try:
            from google.genai import types

            aspect_ratio = self._get_aspect_ratio(request.width, request.height)

            response = client.models.generate_content(
                model=self._image_model,
                contents=[request.prompt],
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size="1K",
                    ),
                ),
            )

            image_data = self._extract_image_from_response(response)
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
        """Edit an image using Gemini generate_content with reference image.

        If clothing_image is provided, both avatar and clothing images are sent
        to the model for virtual try-on generation.
        """
        if request.reference_image is None:
            raise ValidationError("reference_image is required for edit_image")

        client = self._ensure_client()
        start = time.perf_counter()

        try:
            from google.genai import types

            aspect_ratio = self._get_aspect_ratio(request.width, request.height)

            # Build content list: prompt + images
            contents: list = [request.prompt]

            # Add reference image (avatar)
            ref_mime_type = self._detect_mime_type(request.reference_image)
            ref_image = types.Part(
                inline_data=types.Blob(
                    mime_type=ref_mime_type,
                    data=request.reference_image,
                )
            )
            contents.append(ref_image)

            # Add clothing image if provided (for try-on)
            if request.clothing_image is not None:
                clothing_mime_type = self._detect_mime_type(request.clothing_image)
                clothing_image = types.Part(
                    inline_data=types.Blob(
                        mime_type=clothing_mime_type,
                        data=request.clothing_image,
                    )
                )
                contents.append(clothing_image)

            response = client.models.generate_content(
                model=self._image_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size="1K",
                    ),
                ),
            )

            image_data = self._extract_image_from_response(response)
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

    def _detect_mime_type(self, image_bytes: bytes) -> str:
        """Detect MIME type from image bytes."""
        if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        elif image_bytes[:2] == b"\xff\xd8":
            return "image/jpeg"
        elif image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
            return "image/webp"
        elif image_bytes[:6] in (b"GIF87a", b"GIF89a"):
            return "image/gif"
        else:
            return "image/png"  # Default

    def generate_video(
        self, request: VideoGenerationRequest
    ) -> VideoGenerationResponse:
        """Generate a video using Veo."""
        client = self._ensure_client()
        start = time.perf_counter()

        try:
            import io
            from google.genai import types

            # Ensure image is bytes and detect mime type
            image_bytes = request.image
            mime_type = self._detect_mime_type(image_bytes)

            # Create the specific wrapper expected by the Google SDK for video generation
            formatted_image = types.Image(
                image_bytes=image_bytes,
                mime_type=mime_type,
            )

            # Generate video using Veo
            operation = client.models.generate_videos(
                model=self._video_model,
                prompt=request.prompt,
                image=formatted_image,
                config=types.GenerateVideosConfig(
                    aspect_ratio="9:16",
                    resolution="720p",
                    duration_seconds=int(request.duration_seconds),
                    generate_audio=False,
                ),
            )

            # Poll for completion (video generation is async)
            while not operation.done:
                time.sleep(5)
                operation = client.operations.get(operation)

            # Extract video bytes from the response
            # Response structure: GeneratedVideo(video=Video(video_bytes=bytes, mime_type=str))
            generated_video = operation.result.generated_videos[0]
            video_bytes = generated_video.video.video_bytes
            latency = (time.perf_counter() - start) * 1000

            # Use input image as first frame, last frame from video if available
            first_frame = request.image
            last_frame = request.image  # TODO: Extract actual last frame from video

            return VideoGenerationResponse(
                video=video_bytes,
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
