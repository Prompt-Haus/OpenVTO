"""Storage backends for caching generated assets."""

from openvto.storage.base import CacheEntry, NullStorage, Storage
from openvto.storage.local import LocalStorage
from openvto.storage.memory import MemoryStorage

__all__ = [
    "CacheEntry",
    "LocalStorage",
    "MemoryStorage",
    "NullStorage",
    "Storage",
]
