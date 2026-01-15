"""Hashing utilities for cache key generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    """Hash bytes using specified algorithm.

    Args:
        data: Bytes to hash.
        algorithm: Hash algorithm ("sha256", "md5", "sha1").

    Returns:
        Hex digest of the hash.
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string.

    Args:
        text: String to hash.
        algorithm: Hash algorithm.

    Returns:
        Hex digest of the hash.
    """
    return hash_bytes(text.encode("utf-8"), algorithm)


def hash_file(path: str | Path, algorithm: str = "sha256") -> str:
    """Hash a file's contents.

    Args:
        path: Path to file.
        algorithm: Hash algorithm.

    Returns:
        Hex digest of the hash.
    """
    path = Path(path)
    hasher = hashlib.new(algorithm)

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def hash_dict(data: dict[str, Any], algorithm: str = "sha256") -> str:
    """Hash a dictionary (JSON-serializable).

    Args:
        data: Dictionary to hash.
        algorithm: Hash algorithm.

    Returns:
        Hex digest of the hash.
    """
    # Sort keys for deterministic ordering
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hash_string(serialized, algorithm)


def short_hash(data: bytes | str, length: int = 8) -> str:
    """Generate a short hash for display/logging purposes.

    Args:
        data: Data to hash.
        length: Length of output hash (max 64 for sha256).

    Returns:
        Truncated hex digest.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hash_bytes(data)[:length]
