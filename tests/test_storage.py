"""Tests for OpenVTO storage backends."""

import tempfile
from pathlib import Path

import pytest

from openvto.storage import (
    CacheEntry,
    LocalStorage,
    MemoryStorage,
    NullStorage,
)


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        from datetime import datetime

        entry = CacheEntry(
            key="test_key",
            created_at=datetime.now(),
            size_bytes=1024,
            content_type="image/png",
            metadata={"model": "test"},
        )
        data = entry.to_dict()
        restored = CacheEntry.from_dict(data)

        assert restored.key == entry.key
        assert restored.size_bytes == entry.size_bytes
        assert restored.content_type == entry.content_type
        assert restored.metadata == entry.metadata


class TestNullStorage:
    """Tests for NullStorage (no-op cache)."""

    def test_get_returns_none(self):
        """Test get always returns None."""
        storage = NullStorage()
        assert storage.get("any_key") is None

    def test_exists_returns_false(self):
        """Test exists always returns False."""
        storage = NullStorage()
        storage.put("key", b"data")
        assert storage.exists("key") is False

    def test_put_returns_entry(self):
        """Test put returns valid entry."""
        storage = NullStorage()
        entry = storage.put("key", b"data", content_type="text/plain")
        assert entry.key == "key"
        assert entry.size_bytes == 4


class TestMemoryStorage:
    """Tests for MemoryStorage."""

    def test_put_and_get(self):
        """Test basic put/get operations."""
        storage = MemoryStorage()
        storage.put("key1", b"data1")
        assert storage.get("key1") == b"data1"

    def test_exists(self):
        """Test exists check."""
        storage = MemoryStorage()
        assert storage.exists("key1") is False
        storage.put("key1", b"data")
        assert storage.exists("key1") is True

    def test_delete(self):
        """Test delete operation."""
        storage = MemoryStorage()
        storage.put("key1", b"data")
        assert storage.delete("key1") is True
        assert storage.exists("key1") is False
        assert storage.delete("key1") is False

    def test_clear(self):
        """Test clear operation."""
        storage = MemoryStorage()
        storage.put("key1", b"data1")
        storage.put("key2", b"data2")
        count = storage.clear()
        assert count == 2
        assert storage.count() == 0

    def test_list_keys(self):
        """Test listing keys."""
        storage = MemoryStorage()
        storage.put("avatar_1", b"data")
        storage.put("avatar_2", b"data")
        storage.put("tryon_1", b"data")

        all_keys = storage.list_keys()
        assert len(all_keys) == 3

        avatar_keys = storage.list_keys(prefix="avatar_")
        assert len(avatar_keys) == 2

    def test_get_entry(self):
        """Test getting entry metadata."""
        storage = MemoryStorage()
        storage.put("key1", b"data", content_type="image/png", metadata={"test": True})
        entry = storage.get_entry("key1")
        assert entry is not None
        assert entry.content_type == "image/png"
        assert entry.metadata == {"test": True}

    def test_max_entries_eviction(self):
        """Test LRU eviction by entry count."""
        storage = MemoryStorage(max_entries=2)
        storage.put("key1", b"data1")
        storage.put("key2", b"data2")
        storage.put("key3", b"data3")  # Should evict key1

        assert storage.count() == 2
        assert storage.exists("key1") is False
        assert storage.exists("key2") is True
        assert storage.exists("key3") is True

    def test_max_size_eviction(self):
        """Test LRU eviction by size."""
        storage = MemoryStorage(max_size_bytes=100)
        storage.put("key1", b"x" * 50)
        storage.put("key2", b"x" * 50)
        storage.put("key3", b"x" * 50)  # Should evict key1

        assert storage.exists("key1") is False
        assert storage.size() <= 100

    def test_size_and_count(self):
        """Test size and count methods."""
        storage = MemoryStorage()
        storage.put("key1", b"data1")
        storage.put("key2", b"data2data2")

        assert storage.count() == 2
        assert storage.size() == 15  # 5 + 10 bytes


class TestLocalStorage:
    """Tests for LocalStorage."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_put_and_get(self, temp_cache_dir):
        """Test basic put/get operations."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("key1", b"data1")
        assert storage.get("key1") == b"data1"

    def test_exists(self, temp_cache_dir):
        """Test exists check."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        assert storage.exists("key1") is False
        storage.put("key1", b"data")
        assert storage.exists("key1") is True

    def test_delete(self, temp_cache_dir):
        """Test delete operation."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("key1", b"data")
        assert storage.delete("key1") is True
        assert storage.exists("key1") is False

    def test_clear(self, temp_cache_dir):
        """Test clear operation."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("key1", b"data1")
        storage.put("key2", b"data2")
        count = storage.clear()
        assert count == 2
        assert storage.count() == 0

    def test_list_keys(self, temp_cache_dir):
        """Test listing keys."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("avatar_1", b"data")
        storage.put("avatar_2", b"data")
        storage.put("tryon_1", b"data")

        all_keys = storage.list_keys()
        assert len(all_keys) == 3

        avatar_keys = storage.list_keys(prefix="avatar_")
        assert len(avatar_keys) == 2

    def test_get_entry(self, temp_cache_dir):
        """Test getting entry metadata."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("key1", b"data", content_type="image/png", metadata={"test": True})
        entry = storage.get_entry("key1")
        assert entry is not None
        assert entry.content_type == "image/png"
        assert entry.metadata == {"test": True}

    def test_prune_by_entries(self, temp_cache_dir):
        """Test pruning by entry count."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("key1", b"data1")
        storage.put("key2", b"data2")
        storage.put("key3", b"data3")

        removed = storage.prune(max_entries=2)
        assert removed == 1
        assert storage.count() == 2

    def test_prune_by_size(self, temp_cache_dir):
        """Test pruning by total size."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("key1", b"x" * 100)
        storage.put("key2", b"x" * 100)
        storage.put("key3", b"x" * 100)

        removed = storage.prune(max_size_bytes=200)
        assert removed >= 1
        assert storage.size() <= 200

    def test_files_created(self, temp_cache_dir):
        """Test that data and meta files are created."""
        storage = LocalStorage(cache_dir=temp_cache_dir)
        storage.put("test_key", b"test_data")

        data_files = list(temp_cache_dir.glob("*.data"))
        meta_files = list(temp_cache_dir.glob("*.meta.json"))

        assert len(data_files) == 1
        assert len(meta_files) == 1

    def test_persistence(self, temp_cache_dir):
        """Test that data persists across instances."""
        storage1 = LocalStorage(cache_dir=temp_cache_dir)
        storage1.put("key1", b"persistent_data")

        # Create new instance pointing to same directory
        storage2 = LocalStorage(cache_dir=temp_cache_dir)
        assert storage2.get("key1") == b"persistent_data"
