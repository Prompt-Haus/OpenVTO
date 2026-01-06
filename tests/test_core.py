"""Tests for OpenVTO core functionality."""

from openvto import OpenVTO, __version__
from openvto.types import ClothingItem, GenerationMeta, Outfit


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.0.1"


def test_client_initialization():
    """Test that OpenVTO client initializes with defaults."""
    vto = OpenVTO()
    assert vto.provider_name == "google"
    assert vto.image_model == "imagen"
    assert vto.video_model == "veo"
    assert vto.cache_enabled is True
    assert vto.prompt_preset == "studio_v1"


def test_client_custom_config():
    """Test that OpenVTO client accepts custom configuration."""
    vto = OpenVTO(
        provider="mock",
        image_model="imagen-pro",
        video_model="veo-fast",
        cache_enabled=False,
        prompt_preset="custom_v1",
    )
    assert vto.provider_name == "mock"
    assert vto.image_model == "imagen-pro"
    assert vto.video_model == "veo-fast"
    assert vto.cache_enabled is False
    assert vto.prompt_preset == "custom_v1"


def test_clothing_item_creation():
    """Test ClothingItem dataclass."""
    item = ClothingItem(
        id="shirt-001",
        image="path/to/shirt.jpg",
        description="White cotton shirt",
        category="top",
        tags=["casual", "summer"],
    )
    assert item.id == "shirt-001"
    assert item.description == "White cotton shirt"
    assert item.category == "top"
    assert "casual" in item.tags


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
        model="imagen",
        provider="google",
        seed=42,
        latency_ms=1500.0,
        cache_hit=False,
    )
    assert meta.model == "imagen"
    assert meta.provider == "google"
    assert meta.seed == 42
    assert meta.latency_ms == 1500.0
    assert meta.cache_hit is False
