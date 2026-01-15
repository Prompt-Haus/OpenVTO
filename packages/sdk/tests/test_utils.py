"""Tests for OpenVTO utilities."""

import time

from openvto.utils import (
    Profiler,
    Timer,
    decode_base64,
    encode_base64,
    format_duration,
    get_image_format,
    hash_bytes,
    hash_dict,
    hash_string,
    short_hash,
    timed,
)


class TestHashing:
    """Tests for hashing utilities."""

    def test_hash_bytes(self):
        """Test hashing bytes."""
        data = b"test data"
        h1 = hash_bytes(data)
        h2 = hash_bytes(data)
        assert h1 == h2
        assert len(h1) == 64  # SHA256 hex

    def test_hash_string(self):
        """Test hashing strings."""
        h = hash_string("hello world")
        assert len(h) == 64

    def test_hash_dict(self):
        """Test hashing dictionaries."""
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}  # Same content, different order
        assert hash_dict(d1) == hash_dict(d2)

    def test_short_hash(self):
        """Test short hash generation."""
        h = short_hash(b"test", length=8)
        assert len(h) == 8


class TestImages:
    """Tests for image utilities."""

    def test_encode_decode_base64(self):
        """Test base64 encoding/decoding roundtrip."""
        original = b"test image data"
        encoded = encode_base64(original)
        decoded = decode_base64(encoded)
        assert decoded == original

    def test_get_image_format_png(self):
        """Test PNG format detection."""
        png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        assert get_image_format(png_header) == "PNG"

    def test_get_image_format_jpeg(self):
        """Test JPEG format detection."""
        jpeg_header = b"\xff\xd8\xff" + b"\x00" * 100
        assert get_image_format(jpeg_header) == "JPEG"

    def test_get_image_format_unknown(self):
        """Test unknown format detection."""
        assert get_image_format(b"random data") == "UNKNOWN"


class TestTiming:
    """Tests for timing utilities."""

    def test_timer_basic(self):
        """Test basic timer functionality."""
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        elapsed = timer.stop()
        assert elapsed >= 10  # At least 10ms
        assert elapsed < 100  # Less than 100ms

    def test_timer_elapsed_ms(self):
        """Test elapsed_ms property."""
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        assert timer.elapsed_ms >= 10

    def test_timed_context_manager(self):
        """Test timed context manager."""
        with timed("test_op") as result:
            time.sleep(0.01)

        assert result.name == "test_op"
        assert result.duration_ms >= 10

    def test_format_duration_ms(self):
        """Test formatting milliseconds."""
        assert format_duration(50) == "50ms"
        assert format_duration(500) == "500ms"

    def test_format_duration_seconds(self):
        """Test formatting seconds."""
        assert format_duration(1500) == "1.5s"
        assert format_duration(5000) == "5.0s"

    def test_format_duration_minutes(self):
        """Test formatting minutes."""
        assert format_duration(90000) == "1m 30s"
        assert format_duration(120000) == "2m 0s"

    def test_profiler(self):
        """Test profiler tracking multiple operations."""
        profiler = Profiler()

        with profiler.track("step1"):
            time.sleep(0.01)

        with profiler.track("step2"):
            time.sleep(0.01)

        assert len(profiler.timings.steps) == 2
        assert profiler.timings.get("step1") is not None
        assert profiler.timings.get("step2") is not None
        assert profiler.timings.total_ms >= 20

    def test_profiler_report(self):
        """Test profiler report generation."""
        profiler = Profiler()
        with profiler.track("operation"):
            pass
        report = profiler.report()
        assert "Total:" in report
        assert "operation:" in report
