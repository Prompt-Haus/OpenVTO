"""In-memory storage backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from openvto.storage.base import CacheEntry, Storage


class MemoryStorage(Storage):
    """In-memory storage backend.

    Stores cached data in a dictionary. Data is lost when the process exits.
    Useful for:
    - Testing
    - Short-lived processes
    - When disk I/O should be avoided

    Attributes:
        max_size_bytes: Optional maximum total cache size.
        max_entries: Optional maximum number of entries.
    """

    def __init__(
        self,
        *,
        max_size_bytes: int | None = None,
        max_entries: int | None = None,
    ) -> None:
        """Initialize memory storage.

        Args:
            max_size_bytes: Maximum total cache size in bytes.
            max_entries: Maximum number of cached entries.
        """
        self._data: dict[str, bytes] = {}
        self._entries: dict[str, CacheEntry] = {}
        self._access_order: list[str] = []  # For LRU eviction
        self.max_size_bytes = max_size_bytes
        self.max_entries = max_entries

    def _update_access(self, key: str) -> None:
        """Update access order for LRU tracking."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def _evict_if_needed(self, new_size: int = 0) -> None:
        """Evict oldest entries if limits exceeded."""
        # Check entry count limit
        while self.max_entries and len(self._data) >= self.max_entries:
            if self._access_order:
                oldest_key = self._access_order[0]
                self.delete(oldest_key)
            else:
                break

        # Check size limit
        if self.max_size_bytes:
            current_size = sum(e.size_bytes for e in self._entries.values())
            while current_size + new_size > self.max_size_bytes and self._access_order:
                oldest_key = self._access_order[0]
                oldest_entry = self._entries.get(oldest_key)
                if oldest_entry:
                    current_size -= oldest_entry.size_bytes
                self.delete(oldest_key)

    def get(self, key: str) -> bytes | None:
        """Retrieve cached data by key."""
        data = self._data.get(key)
        if data is not None:
            self._update_access(key)
        return data

    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, Any] | None = None,
    ) -> CacheEntry:
        """Store data with key."""
        # Evict old entries if needed
        self._evict_if_needed(len(data))

        entry = CacheEntry(
            key=key,
            created_at=datetime.now(),
            size_bytes=len(data),
            content_type=content_type,
            metadata=metadata,
        )

        self._data[key] = data
        self._entries[key] = entry
        self._update_access(key)

        return entry

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._data

    def delete(self, key: str) -> bool:
        """Delete cached data by key."""
        existed = key in self._data
        self._data.pop(key, None)
        self._entries.pop(key, None)
        if key in self._access_order:
            self._access_order.remove(key)
        return existed

    def get_entry(self, key: str) -> CacheEntry | None:
        """Get cache entry metadata without data."""
        return self._entries.get(key)

    def clear(self) -> int:
        """Clear all cached data."""
        count = len(self._data)
        self._data.clear()
        self._entries.clear()
        self._access_order.clear()
        return count

    def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys, optionally filtered by prefix."""
        if not prefix:
            return sorted(self._data.keys())
        return sorted(k for k in self._data.keys() if k.startswith(prefix))

    def size(self) -> int:
        """Get total size of cached data in bytes."""
        return sum(e.size_bytes for e in self._entries.values())

    def count(self) -> int:
        """Get number of cached entries."""
        return len(self._data)
