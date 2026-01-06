"""Local filesystem storage backend."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from openvto.errors import CacheError
from openvto.storage.base import CacheEntry, Storage

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".openvto" / "cache"


class LocalStorage(Storage):
    """Filesystem-based storage backend.

    Stores cached data in a local directory with metadata JSON sidecars.
    Directory structure:
        cache_dir/
            {key}.data          # Raw cached data
            {key}.meta.json     # Metadata (CacheEntry)

    Attributes:
        cache_dir: Path to cache directory.
    """

    def __init__(self, cache_dir: str | Path | None = None) -> None:
        """Initialize local storage.

        Args:
            cache_dir: Directory for cache storage.
                       Defaults to ~/.openvto/cache
        """
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise CacheError(f"Failed to create cache directory: {e}")

    def _data_path(self, key: str) -> Path:
        """Get path for data file."""
        # Sanitize key for filesystem
        safe_key = self._sanitize_key(key)
        return self.cache_dir / f"{safe_key}.data"

    def _meta_path(self, key: str) -> Path:
        """Get path for metadata file."""
        safe_key = self._sanitize_key(key)
        return self.cache_dir / f"{safe_key}.meta.json"

    def _sanitize_key(self, key: str) -> str:
        """Sanitize key for use as filename."""
        # Replace problematic characters
        safe = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        # Limit length
        if len(safe) > 200:
            safe = safe[:200]
        return safe

    def get(self, key: str) -> bytes | None:
        """Retrieve cached data by key."""
        data_path = self._data_path(key)
        if not data_path.exists():
            return None
        try:
            return data_path.read_bytes()
        except OSError as e:
            raise CacheError(f"Failed to read cache entry: {e}")

    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, Any] | None = None,
    ) -> CacheEntry:
        """Store data with key."""
        data_path = self._data_path(key)
        meta_path = self._meta_path(key)

        entry = CacheEntry(
            key=key,
            created_at=datetime.now(),
            size_bytes=len(data),
            content_type=content_type,
            metadata=metadata,
        )

        try:
            # Write data
            data_path.write_bytes(data)
            # Write metadata
            meta_path.write_text(json.dumps(entry.to_dict(), indent=2))
        except OSError as e:
            # Clean up on failure
            data_path.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)
            raise CacheError(f"Failed to write cache entry: {e}")

        return entry

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self._data_path(key).exists()

    def delete(self, key: str) -> bool:
        """Delete cached data by key."""
        data_path = self._data_path(key)
        meta_path = self._meta_path(key)

        existed = data_path.exists()
        data_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)
        return existed

    def get_entry(self, key: str) -> CacheEntry | None:
        """Get cache entry metadata without data."""
        meta_path = self._meta_path(key)
        if not meta_path.exists():
            return None
        try:
            data = json.loads(meta_path.read_text())
            return CacheEntry.from_dict(data)
        except (OSError, json.JSONDecodeError, KeyError) as e:
            # Corrupted metadata - try to reconstruct from data file
            data_path = self._data_path(key)
            if data_path.exists():
                stat = data_path.stat()
                return CacheEntry(
                    key=key,
                    created_at=datetime.fromtimestamp(stat.st_mtime),
                    size_bytes=stat.st_size,
                )
            return None

    def clear(self) -> int:
        """Clear all cached data."""
        count = 0
        for key in self.list_keys():
            if self.delete(key):
                count += 1
        return count

    def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys, optionally filtered by prefix."""
        keys = []
        try:
            for path in self.cache_dir.glob("*.meta.json"):
                meta_data = json.loads(path.read_text())
                key = meta_data.get("key", path.stem.replace(".meta", ""))
                if not prefix or key.startswith(prefix):
                    keys.append(key)
        except OSError:
            pass
        return sorted(keys)

    def cleanup_orphans(self) -> int:
        """Remove orphaned data files without metadata.

        Returns:
            Number of orphaned files removed.
        """
        removed = 0
        try:
            for data_path in self.cache_dir.glob("*.data"):
                meta_path = data_path.with_suffix(".meta.json")
                if not meta_path.exists():
                    data_path.unlink()
                    removed += 1
        except OSError:
            pass
        return removed

    def prune(
        self, max_size_bytes: int | None = None, max_entries: int | None = None
    ) -> int:
        """Prune cache to stay within limits.

        Removes oldest entries first.

        Args:
            max_size_bytes: Maximum total cache size.
            max_entries: Maximum number of entries.

        Returns:
            Number of entries removed.
        """
        if not max_size_bytes and not max_entries:
            return 0

        # Get all entries with timestamps
        entries = []
        for key in self.list_keys():
            entry = self.get_entry(key)
            if entry:
                entries.append(entry)

        # Sort by creation time (oldest first)
        entries.sort(key=lambda e: e.created_at)

        removed = 0
        current_size = sum(e.size_bytes for e in entries)
        current_count = len(entries)

        for entry in entries:
            should_remove = False

            if max_size_bytes and current_size > max_size_bytes:
                should_remove = True
            if max_entries and current_count > max_entries:
                should_remove = True

            if should_remove:
                self.delete(entry.key)
                current_size -= entry.size_bytes
                current_count -= 1
                removed += 1
            else:
                break

        return removed
