"""Tests for OpenVTO providers."""

from openvto.providers import (
    ImageGenerationRequest,
    MockProvider,
    VideoGenerationRequest,
)


def test_mock_provider_name():
    """Test mock provider returns correct name."""
    provider = MockProvider()
    assert provider.name == "mock"


def test_mock_provider_validate_api_key():
    """Test mock provider always validates."""
    provider = MockProvider()
    assert provider.validate_api_key() is True


def test_mock_generate_image():
    """Test mock image generation returns valid response."""
    provider = MockProvider(latency_ms=10)
    request = ImageGenerationRequest(
        prompt="test prompt",
        width=512,
        height=512,
        seed=42,
    )
    response = provider.generate_image(request)

    assert response.image is not None
    assert len(response.image) > 0
    assert response.width == 512
    assert response.height == 512
    assert response.seed == 42
    assert response.model == "mock-image"
    assert response.latency_ms is not None


def test_mock_generate_image_deterministic():
    """Test mock image generation is deterministic with same seed."""
    provider = MockProvider(latency_ms=1)
    request = ImageGenerationRequest(prompt="test", seed=123)

    response1 = provider.generate_image(request)
    response2 = provider.generate_image(request)

    assert response1.image == response2.image


def test_mock_edit_image():
    """Test mock image editing returns valid response."""
    provider = MockProvider(latency_ms=10)
    request = ImageGenerationRequest(
        prompt="edit prompt",
        reference_image=b"fake image data",
        seed=42,
    )
    response = provider.edit_image(request)

    assert response.image is not None
    assert len(response.image) > 0


def test_mock_generate_video():
    """Test mock video generation returns valid response."""
    provider = MockProvider(latency_ms=10)
    request = VideoGenerationRequest(
        prompt="video prompt",
        image=b"fake image",
        duration_seconds=4.0,
        seed=42,
    )
    response = provider.generate_video(request)

    assert response.video is not None
    assert len(response.video) > 0
    assert response.first_frame is not None
    assert response.last_frame is not None
    assert response.duration_seconds == 4.0
    assert response.seed == 42
    assert response.model == "mock-video"


def test_mock_generate_video_deterministic():
    """Test mock video generation is deterministic with same seed."""
    provider = MockProvider(latency_ms=1)
    request = VideoGenerationRequest(prompt="test", image=b"img", seed=456)

    response1 = provider.generate_video(request)
    response2 = provider.generate_video(request)

    assert response1.video == response2.video
    assert response1.first_frame == response2.first_frame
