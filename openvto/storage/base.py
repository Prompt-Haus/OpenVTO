"""Base storage interface for caching generated assets."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class CacheEntry:
    """Metadata for a cached item.

    Attributes:
        key: Cache key.
        created_at: When the entry was created.
        size_bytes: Size of cached data in bytes.
        content_type: MIME type or format of cached data.
        metadata: Additional metadata (prompt, model, etc.).
    """

    key: str
    created_at: datetime
    size_bytes: int
    content_type: str = "application/octet-stream"
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class Storage(ABC):
    """Abstract base class for storage backends.

    Storage implementations handle caching of generated images and videos
    to avoid redundant API calls and enable reproducibility.
    """

    @abstractmethod
    def get(self, key: str) -> bytes | None:
        """Retrieve cached data by key.

        Args:
            key: Cache key.

        Returns:
            Cached bytes if found, None otherwise.
        """
        ...

    @abstractmethod
    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, Any] | None = None,
    ) -> CacheEntry:
        """Store data with key.

        Args:
            key: Cache key.
            data: Data to cache.
            content_type: MIME type of the data.
            metadata: Additional metadata to store.

        Returns:
            CacheEntry with storage metadata.
        """
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key.

        Returns:
            True if key exists, False otherwise.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete cached data by key.

        Args:
            key: Cache key.

        Returns:
            True if deleted, False if key didn't exist.
        """
        ...

    @abstractmethod
    def get_entry(self, key: str) -> CacheEntry | None:
        """Get cache entry metadata without data.

        Args:
            key: Cache key.

        Returns:
            CacheEntry if found, None otherwise.
        """
        ...

    def get_with_entry(self, key: str) -> tuple[bytes | None, CacheEntry | None]:
        """Get both data and entry metadata.

        Args:
            key: Cache key.

        Returns:
            Tuple of (data, entry), both None if not found.
        """
        data = self.get(key)
        if data is None:
            return None, None
        entry = self.get_entry(key)
        return data, entry

    @abstractmethod
    def clear(self) -> int:
        """Clear all cached data.

        Returns:
            Number of entries cleared.
        """
        ...

    @abstractmethod
    def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys, optionally filtered by prefix.

        Args:
            prefix: Optional prefix to filter keys.

        Returns:
            List of matching keys.
        """
        ...

    def size(self) -> int:
        """Get total size of cached data in bytes.

        Returns:
            Total size in bytes.
        """
        total = 0
        for key in self.list_keys():
            entry = self.get_entry(key)
            if entry:
                total += entry.size_bytes
        return total

    def count(self) -> int:
        """Get number of cached entries.

        Returns:
            Number of entries.
        """
        return len(self.list_keys())


class NullStorage(Storage):
    """No-op storage that doesn't cache anything.

    Useful for disabling caching without changing code.
    """

    def get(self, key: str) -> bytes | None:
        return None

    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, Any] | None = None,
    ) -> CacheEntry:
        return CacheEntry(
            key=key,
            created_at=datetime.now(),
            size_bytes=len(data),
            content_type=content_type,
            metadata=metadata,
        )

    def exists(self, key: str) -> bool:
        return False

    def delete(self, key: str) -> bool:
        return False

    def get_entry(self, key: str) -> CacheEntry | None:
        return None

    def clear(self) -> int:
        return 0

    def list_keys(self, prefix: str = "") -> list[str]:
        return []

