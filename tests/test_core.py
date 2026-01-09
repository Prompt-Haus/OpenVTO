"""Tests for OpenVTO core functionality."""

from openvto import OpenVTO, __version__
from openvto.types import ClothingItem, GenerationMeta, ImageModel, Outfit, VideoModel


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_client_initialization_with_mock():
    """Test that OpenVTO client initializes with mock provider."""
    vto = OpenVTO(provider="mock", cache_enabled=False)
    assert vto.provider_name == "mock"
    assert vto.image_model == ImageModel.NANO_BANANA_PRO.value
    assert vto.video_model == VideoModel.VEO_31_FAST.value
    assert vto.cache_enabled is False
    assert vto.prompt_preset == "studio_v1"
    assert vto.provider.name == "mock"


def test_client_custom_config():
    """Test that OpenVTO client accepts custom configuration."""
    vto = OpenVTO(
        provider="mock",
        image_model=ImageModel.NANO_BANANA_PRO.value,
        video_model=VideoModel.VEO_31_FAST.value,
        cache_enabled=False,
        prompt_preset="custom_v1",
    )
    assert vto.provider_name == "mock"
    assert vto.image_model == ImageModel.NANO_BANANA_PRO.value
    assert vto.video_model == VideoModel.VEO_31_FAST.value
    assert vto.cache_enabled is False
    assert vto.prompt_preset == "custom_v1"


def test_clothing_item_creation():
    """Test ClothingItem dataclass."""
    item = ClothingItem(
        id="shirt-001",
        image="path/to/shirt.jpg",
        name="White Cotton Shirt",
        description="Classic fit cotton shirt",
        styling="oversized",
        category="top",
    )
    assert item.id == "shirt-001"
    assert item.name == "White Cotton Shirt"
    assert item.description == "Classic fit cotton shirt"
    assert item.styling == "oversized"
    assert item.category == "top"


def test_outfit_creation():
    """Test Outfit dataclass."""
    shirt = ClothingItem(id="shirt-001", image="shirt.jpg")
    pants = ClothingItem(id="pants-001", image="pants.jpg")
    outfit = Outfit(items=[shirt, pants], name="Casual Look")

    assert len(outfit.items) == 2
    assert outfit.name == "Casual Look"


def test_outfit_requires_items():
    """Test that Outfit requires at least one item."""
    import pytest

    with pytest.raises(ValueError, match="at least one"):
        Outfit(items=[])


def test_generation_meta():
    """Test GenerationMeta dataclass."""
    meta = GenerationMeta(
        model="gemini-2.5-flash-image",
        provider="google",
        seed=42,
        latency_ms=1500.0,
        cache_hit=False,
    )
    assert meta.model == "gemini-2.5-flash-image"
    assert meta.provider == "google"
    assert meta.seed == 42
    assert meta.latency_ms == 1500.0
    assert meta.cache_hit is False
