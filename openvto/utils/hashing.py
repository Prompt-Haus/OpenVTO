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


def generate_cache_key(
    *components: bytes | str | dict | None,
    prefix: str = "",
    algorithm: str = "sha256",
) -> str:
    """Generate a cache key from multiple components.

    Args:
        *components: Components to include in the key (bytes, str, dict, or None).
        prefix: Optional prefix for the key.
        algorithm: Hash algorithm.

    Returns:
        Cache key string.

    Example:
        >>> key = generate_cache_key(
        ...     selfie_bytes,
        ...     posture_bytes,
        ...     {"background": "studio", "prompt_version": "v1"},
        ...     prefix="avatar"
        ... )
        >>> # Returns: "avatar_a1b2c3d4e5..."
    """
    hasher = hashlib.new(algorithm)

    for component in components:
        if component is None:
            hasher.update(b"__none__")
        elif isinstance(component, bytes):
            hasher.update(component)
        elif isinstance(component, str):
            hasher.update(component.encode("utf-8"))
        elif isinstance(component, dict):
            serialized = json.dumps(component, sort_keys=True, separators=(",", ":"))
            hasher.update(serialized.encode("utf-8"))
        else:
            # Try to convert to string
            hasher.update(str(component).encode("utf-8"))

        # Add separator between components
        hasher.update(b"|")

    digest = hasher.hexdigest()

    if prefix:
        return f"{prefix}_{digest}"
    return digest


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


def generate_avatar_cache_key(
    selfie_bytes: bytes,
    posture_bytes: bytes,
    background: str,
    prompt_version: str,
) -> str:
    """Generate cache key for avatar generation.

    Args:
        selfie_bytes: Selfie image bytes.
        posture_bytes: Posture image bytes.
        background: Background style.
        prompt_version: Prompt template version.

    Returns:
        Cache key for avatar.
    """
    return generate_cache_key(
        selfie_bytes,
        posture_bytes,
        {"background": background, "prompt_version": prompt_version},
        prefix="avatar",
    )


def generate_tryon_cache_key(
    avatar_bytes: bytes,
    clothing_bytes: bytes,
    prompt_version: str,
) -> str:
    """Generate cache key for try-on generation.

    Args:
        avatar_bytes: Avatar image bytes.
        clothing_bytes: Clothing composite image bytes.
        prompt_version: Prompt template version.

    Returns:
        Cache key for try-on.
    """
    return generate_cache_key(
        avatar_bytes,
        clothing_bytes,
        {"prompt_version": prompt_version},
        prefix="tryon",
    )


def generate_video_cache_key(
    image_bytes: bytes,
    mode: str,
    duration_seconds: float,
    prompt_version: str,
) -> str:
    """Generate cache key for video generation.

    Args:
        image_bytes: Source image bytes.
        mode: Video loop mode.
        duration_seconds: Video duration.
        prompt_version: Prompt template version.

    Returns:
        Cache key for video.
    """
    return generate_cache_key(
        image_bytes,
        {
            "mode": mode,
            "duration_seconds": duration_seconds,
            "prompt_version": prompt_version,
        },
        prefix="video",
    )
