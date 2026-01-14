"""Tests for OpenVTO pipelines."""

import pytest

from openvto import OpenVTO
from openvto.pipelines import (
    compose_clothing,
    generate_avatar,
    generate_tryon,
    generate_videoloop,
)
from openvto.providers import MockProvider
from openvto.types import ClothingItem, Outfit


# Create a minimal valid PNG for testing
def create_test_image() -> bytes:
    """Create a minimal test PNG image."""
    import struct
    import zlib

    width, height = 100, 100

    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

    # IDAT - simple red image
    raw_data = b""
    for _ in range(height):
        raw_data += b"\x00" + bytes([255, 0, 0]) * width

    compressed = zlib.compress(raw_data, 9)
    idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF
    idat = (
        struct.pack(">I", len(compressed))
        + b"IDAT"
        + compressed
        + struct.pack(">I", idat_crc)
    )

    # IEND
    iend_crc = zlib.crc32(b"IEND") & 0xFFFFFFFF
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

    return signature + ihdr + idat + iend


class TestGenerateAvatar:
    """Tests for avatar generation pipeline."""

    def test_generate_avatar_basic(self):
        """Test basic avatar generation."""
        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        result = generate_avatar(
            selfie=test_image,
            posture=test_image,
            provider=provider,
        )

        assert result.avatar is not None
        assert result.avatar.image is not None
        assert len(result.avatar.image) > 0
        assert result.meta is not None

    def test_generate_avatar_different_backgrounds(self):
        """Test avatar generation with different backgrounds."""
        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        result_studio = generate_avatar(
            selfie=test_image,
            posture=test_image,
            provider=provider,
            background="studio",
        )
        assert result_studio.avatar.background.value == "studio"

        result_white = generate_avatar(
            selfie=test_image,
            posture=test_image,
            provider=provider,
            background="white",
        )
        assert result_white.avatar.background.value == "white"


class TestGenerateTryon:
    """Tests for try-on generation pipeline."""

    def test_generate_tryon_basic(self):
        """Test basic try-on generation."""
        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        result = generate_tryon(
            avatar=test_image,
            clothes=[test_image],
            provider=provider,
        )

        assert result.try_on is not None
        assert result.image is not None
        assert result.meta is not None

    def test_generate_tryon_with_clothing_items(self):
        """Test try-on with ClothingItem objects."""
        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        items = [
            ClothingItem(id="shirt", image=test_image, name="White Shirt"),
            ClothingItem(id="pants", image=test_image, name="Blue Jeans"),
        ]

        result = generate_tryon(
            avatar=test_image,
            clothes=items,
            provider=provider,
        )

        assert result.try_on is not None

    def test_generate_tryon_with_outfit(self):
        """Test try-on with Outfit object."""
        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        outfit = Outfit(
            items=[ClothingItem(id="dress", image=test_image, name="Summer Dress")],
            name="Summer Look",
        )

        result = generate_tryon(
            avatar=test_image,
            clothes=outfit,
            provider=provider,
        )

        assert result.try_on is not None


class TestGenerateVideoloop:
    """Tests for video loop generation pipeline."""

    def test_generate_videoloop_basic(self):
        """Test basic video loop generation."""
        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        result = generate_videoloop(
            static_image=test_image,
            provider=provider,
            seconds=4.0,
        )

        assert result.video is not None
        assert result.first_frame is not None
        assert result.last_frame is not None
        assert result.duration_seconds == 4.0

    def test_generate_videoloop_modes(self):
        """Test video loop with different modes."""
        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        result_360 = generate_videoloop(
            static_image=test_image,
            provider=provider,
            mode="360",
        )
        assert result_360.mode.value == "360"

        result_idle = generate_videoloop(
            static_image=test_image,
            provider=provider,
            mode="idle",
        )
        assert result_idle.mode.value == "idle"

    def test_generate_videoloop_invalid_duration(self):
        """Test video loop with invalid duration raises error."""
        from openvto.errors import ValidationError

        provider = MockProvider(latency_ms=1)
        test_image = create_test_image()

        with pytest.raises(ValidationError):
            generate_videoloop(
                static_image=test_image,
                provider=provider,
                seconds=2.0,  # Too short
            )


class TestComposeClothing:
    """Tests for clothing composition."""

    def test_compose_single_item(self):
        """Test composing single item (passthrough)."""
        test_image = create_test_image()
        item = ClothingItem(id="shirt", image=test_image, name="Shirt")

        result = compose_clothing([item])

        assert result.item_count == 1
        assert result.layout == "single"

    def test_compose_multiple_items(self):
        """Test composing multiple items."""
        pytest.importorskip("PIL")

        test_image = create_test_image()
        items = [
            ClothingItem(id="shirt", image=test_image, name="Shirt"),
            ClothingItem(id="pants", image=test_image, name="Pants"),
        ]

        result = compose_clothing(items, layout="grid")

        assert result.item_count == 2
        assert result.layout == "grid"
        assert "Shirt" in result.description
        assert "Pants" in result.description

    def test_compose_outfit(self):
        """Test composing from Outfit object."""
        pytest.importorskip("PIL")

        test_image = create_test_image()
        outfit = Outfit(
            items=[
                ClothingItem(id="top", image=test_image, name="Top"),
                ClothingItem(id="bottom", image=test_image, name="Bottom"),
            ]
        )

        result = compose_clothing(outfit, layout="horizontal")

        assert result.item_count == 2
        assert result.layout == "horizontal"


class TestOpenVTOClient:
    """Tests for the main OpenVTO client."""

    def test_client_pipeline(self):
        """Test full pipeline through client."""
        vto = OpenVTO(provider="mock")
        test_image = create_test_image()

        result = vto.pipeline(
            selfie=test_image,
            posture=test_image,
            clothes=[test_image],
            make_video=True,
        )

        assert result.avatar is not None
        assert result.tryon is not None
        assert result.video is not None
        assert result.total_latency_ms is not None
        assert result.static_image is not None
        assert result.has_video is True

    def test_client_pipeline_no_video(self):
        """Test pipeline without video generation."""
        vto = OpenVTO(provider="mock")
        test_image = create_test_image()

        result = vto.pipeline(
            selfie=test_image,
            posture=test_image,
            clothes=[test_image],
            make_video=False,
        )

        assert result.avatar is not None
        assert result.tryon is not None
        assert result.video is None
        assert result.has_video is False

    def test_client_individual_steps(self):
        """Test individual generation steps through client."""
        vto = OpenVTO(provider="mock")
        test_image = create_test_image()

        avatar = vto.generate_avatar(selfie=test_image, posture=test_image)
        assert avatar.avatar is not None

        tryon = vto.generate_tryon(avatar=avatar, clothes=[test_image])
        assert tryon.try_on is not None

        video = vto.generate_videoloop(static_image=tryon)
        assert video.video is not None
