"""Tests for OpenVTO core functionality."""

from openvto import OpenVTO, __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_hello():
    """Test hello world functionality."""
    vto = OpenVTO()
    assert vto.hello() == "Hello from OpenVTO!"

