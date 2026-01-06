"""Mock provider for testing and local development."""

from __future__ import annotations

import hashlib
import struct
import time

from openvto.providers.base import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    Provider,
    VideoGenerationRequest,
    VideoGenerationResponse,
)


def _generate_deterministic_bytes(seed: int, size: int) -> bytes:
    """Generate deterministic bytes from a seed for testing."""
    # Use seed to generate reproducible "random" bytes
    result = []
    current = seed
    for _ in range(size // 4 + 1):
        current = (current * 1103515245 + 12345) & 0x7FFFFFFF
        result.append(struct.pack(">I", current))
    return b"".join(result)[:size]


def _create_minimal_png(width: int, height: int, seed: int) -> bytes:
    """Create a minimal valid PNG for testing.

    Creates a small solid-color PNG that's valid but tiny.
    """
    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk (image header)
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = _crc32(b"IHDR" + ihdr_data)
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

    # Generate color from seed
    r = (seed * 17) % 256
    g = (seed * 31) % 256
    b = (seed * 47) % 256

    # IDAT chunk (image data) - minimal scanlines
    raw_data = b""
    for _ in range(height):
        raw_data += b"\x00"  # Filter byte
        raw_data += bytes([r, g, b]) * width

    # Compress with zlib
    import zlib

    compressed = zlib.compress(raw_data, 9)
    idat_crc = _crc32(b"IDAT" + compressed)
    idat = (
        struct.pack(">I", len(compressed))
        + b"IDAT"
        + compressed
        + struct.pack(">I", idat_crc)
    )

    # IEND chunk
    iend_crc = _crc32(b"IEND")
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

    return signature + ihdr + idat + iend


def _crc32(data: bytes) -> int:
    """Calculate CRC32 for PNG chunk."""
    import zlib

    return zlib.crc32(data) & 0xFFFFFFFF


def _create_minimal_mp4(duration_seconds: float, seed: int) -> bytes:
    """Create minimal MP4 bytes for testing.

    Returns deterministic bytes that represent a "video" for testing purposes.
    Real implementation would create actual MP4 structure.
    """
    # For testing, we just create deterministic bytes with MP4-like header
    header = b"\x00\x00\x00\x1c\x66\x74\x79\x70\x69\x73\x6f\x6d"  # ftyp box start
    size = int(duration_seconds * 1000)  # Approximate size based on duration
    content = _generate_deterministic_bytes(seed, size)
    return header + content


class MockProvider(Provider):
    """Mock provider for testing and local development.

    Generates deterministic fake outputs that are valid image/video formats
    but contain no meaningful visual content. Useful for:
    - Unit tests
    - Local development without API keys
    - CI/CD pipelines
    """

    def __init__(self, latency_ms: float = 100.0) -> None:
        """Initialize mock provider.

        Args:
            latency_ms: Simulated latency in milliseconds.
        """
        self._latency_ms = latency_ms

    @property
    def name(self) -> str:
        return "mock"

    def _get_seed(self, request_seed: int | None, prompt: str) -> int:
        """Get deterministic seed from request or prompt."""
        if request_seed is not None:
            return request_seed
        return int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)

    def generate_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """Generate a mock image."""
        start = time.perf_counter()

        seed = self._get_seed(request.seed, request.prompt)

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        # Generate small but valid PNG
        image = _create_minimal_png(request.width, request.height, seed)

        latency = (time.perf_counter() - start) * 1000

        return ImageGenerationResponse(
            image=image,
            width=request.width,
            height=request.height,
            seed=seed,
            model="mock-image",
            latency_ms=latency,
        )

    def edit_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Edit a mock image (same as generate for mock)."""
        # For mock, editing is the same as generating
        # In real providers, this would use the reference_image
        return self.generate_image(request)

    def generate_video(
        self, request: VideoGenerationRequest
    ) -> VideoGenerationResponse:
        """Generate a mock video."""
        start = time.perf_counter()

        seed = self._get_seed(request.seed, request.prompt)

        # Simulate longer latency for video
        time.sleep(self._latency_ms * 3 / 1000)

        # Generate mock video and frames
        video = _create_minimal_mp4(request.duration_seconds, seed)
        first_frame = _create_minimal_png(request.width, request.height, seed)
        last_frame = _create_minimal_png(request.width, request.height, seed + 1)

        latency = (time.perf_counter() - start) * 1000

        return VideoGenerationResponse(
            video=video,
            first_frame=first_frame,
            last_frame=last_frame,
            duration_seconds=request.duration_seconds,
            width=request.width,
            height=request.height,
            seed=seed,
            model="mock-video",
            latency_ms=latency,
        )

    def validate_api_key(self) -> bool:
        """Mock always has valid credentials."""
        return True
