"""Example assets helper API for OpenVTO.

This module provides convenient access to bundled demo assets for testing
and demonstration purposes.

Example usage:
    >>> from openvto import example
    >>> example.clothes("jackets", i=1)
    {'front': PosixPath('.../1_front.jpg'), 'back': PosixPath('.../1_back.jpg')}
    >>> example.avatar(i=1)
    PosixPath('.../1.png')
    >>> example.person(i=1, kind="posture")
    PosixPath('.../1_posture.jpg')
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

if TYPE_CHECKING:
    from PIL import Image

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files  # type: ignore[import-not-found]


__all__ = [
    "clothes",
    "avatar",
    "person",
    "list_clothes_categories",
    "list_clothes_items",
]


# Valid views for clothing items
VALID_VIEWS = frozenset({"front", "back"})

# Valid person photo kinds
VALID_PERSON_KINDS = frozenset({"posture", "selfie"})

# Return type options
ReturnType = Literal["path", "pil", "bytes"]


def _get_assets_path() -> Path:
    """Get the path to the bundled assets directory.

    Uses importlib.resources to locate assets, which works both in development
    and when installed as a package.
    """
    return Path(files("openvto") / "assets")  # type: ignore[arg-type]


def _validate_category(category: str) -> Path:
    """Validate that a clothing category exists and return its path."""
    assets_path = _get_assets_path()
    category_path = assets_path / "clothes" / category

    if not category_path.exists():
        available = list_clothes_categories()
        raise ValueError(
            f"Unknown clothing category '{category}'. "
            f"Available categories: {', '.join(available)}"
        )
    return category_path


def _validate_view(view: str) -> None:
    """Validate that a view is valid."""
    if view not in VALID_VIEWS:
        raise ValueError(
            f"Invalid view '{view}'. Valid views are: {', '.join(sorted(VALID_VIEWS))}"
        )


def _validate_person_kind(kind: str) -> None:
    """Validate that a person photo kind is valid."""
    if kind not in VALID_PERSON_KINDS:
        raise ValueError(
            f"Invalid kind '{kind}'. Valid kinds are: {', '.join(sorted(VALID_PERSON_KINDS))}"
        )


def _load_asset(path: Path, return_type: ReturnType) -> Path | bytes | "Image.Image":
    """Load an asset with the specified return type."""
    if not path.exists():
        raise FileNotFoundError(f"Asset not found: {path}")

    if return_type == "path":
        return path
    elif return_type == "bytes":
        return path.read_bytes()
    elif return_type == "pil":
        try:
            from PIL import Image
        except ImportError:
            raise ImportError(
                "Pillow is required for return_type='pil'. "
                "Install it with: pip install openvto[examples]"
            ) from None
        return Image.open(path)
    else:
        raise ValueError(
            f"Invalid return_type '{return_type}'. Valid options: 'path', 'bytes', 'pil'"
        )


def list_clothes_categories() -> list[str]:
    """List all available clothing categories.

    Returns:
        List of category names (e.g., ['jackets', 'pants', 'shirts']).

    Example:
        >>> example.list_clothes_categories()
        ['jackets', 'pants', 'shirts']
    """
    clothes_path = _get_assets_path() / "clothes"
    if not clothes_path.exists():
        return []

    return sorted(
        d.name
        for d in clothes_path.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def list_clothes_items(category: str) -> dict[str, list[int] | list[str]]:
    """List all available items in a clothing category.

    Args:
        category: The clothing category (e.g., 'jackets', 'pants', 'shirts').

    Returns:
        Dictionary with 'indices' (list of item numbers) and 'views' (list of view types).

    Raises:
        ValueError: If the category doesn't exist.

    Example:
        >>> example.list_clothes_items("jackets")
        {'indices': [1, 2, 3, 4], 'views': ['back', 'front']}
    """
    category_path = _validate_category(category)

    # Find all indices and views by parsing filenames
    indices: set[int] = set()
    views: set[str] = set()

    for file in category_path.glob("*_*.jpg"):
        parts = file.stem.split("_", 1)
        if len(parts) == 2:
            try:
                indices.add(int(parts[0]))
                views.add(parts[1])
            except ValueError:
                continue

    return {
        "indices": sorted(indices),
        "views": sorted(views),
    }


# Overloads for proper type hints based on arguments
@overload
def clothes(
    category: str,
    i: None = None,
    view: None = None,
    *,
    return_type: ReturnType = "path",
) -> list[dict[str, Any]]: ...


@overload
def clothes(
    category: str,
    i: int,
    view: None = None,
    *,
    return_type: ReturnType = "path",
) -> dict[str, Any]: ...


@overload
def clothes(
    category: str,
    i: int,
    view: str,
    *,
    return_type: ReturnType = "path",
) -> Path | bytes | "Image.Image": ...


def clothes(
    category: str,
    i: int | None = None,
    view: str | None = None,
    *,
    return_type: ReturnType = "path",
) -> list[dict[str, Any]] | dict[str, Any] | Path | bytes | "Image.Image":
    """Get example clothing assets.

    Args:
        category: The clothing category ('jackets', 'pants', or 'shirts').
        i: Optional item index (1-4). If None, returns all items.
        view: Optional view ('front' or 'back'). If None with i, returns both views.
        return_type: How to return assets - 'path' (default), 'pil', or 'bytes'.

    Returns:
        - If i is None: List of dicts with all items, each having 'i', 'front', 'back'.
        - If i is provided but view is None: Dict with 'front' and 'back' paths.
        - If i and view are provided: Single path/Image/bytes.

    Raises:
        ValueError: If category or view is invalid.
        FileNotFoundError: If the requested asset doesn't exist.

    Examples:
        >>> # Get all jackets
        >>> example.clothes("jackets")
        [{'i': 1, 'front': ..., 'back': ...}, ...]

        >>> # Get specific item
        >>> example.clothes("jackets", i=2)
        {'front': ..., 'back': ...}

        >>> # Get specific view
        >>> example.clothes("jackets", i=2, view="front")
        PosixPath('.../2_front.jpg')
    """
    category_path = _validate_category(category)

    if view is not None:
        _validate_view(view)

    # Case 1: Get all items
    if i is None:
        if view is not None:
            raise ValueError("Cannot specify 'view' without specifying 'i'")

        items_info = list_clothes_items(category)
        result: list[dict[str, Any]] = []

        for idx in items_info["indices"]:
            item_dict: dict[str, Any] = {"i": idx}
            for v in VALID_VIEWS:
                asset_path = category_path / f"{idx}_{v}.jpg"
                if asset_path.exists():
                    item_dict[v] = _load_asset(asset_path, return_type)
            result.append(item_dict)

        return result

    # Case 2: Get specific item, all views
    if view is None:
        result_dict: dict[str, Any] = {}
        for v in VALID_VIEWS:
            asset_path = category_path / f"{i}_{v}.jpg"
            if not asset_path.exists():
                raise FileNotFoundError(
                    f"Clothing asset not found: {category}/{i}_{v}.jpg. "
                    f"Available indices: {list_clothes_items(category)['indices']}"
                )
            result_dict[v] = _load_asset(asset_path, return_type)
        return result_dict

    # Case 3: Get specific item and view
    asset_path = category_path / f"{i}_{view}.jpg"
    if not asset_path.exists():
        raise FileNotFoundError(
            f"Clothing asset not found: {category}/{i}_{view}.jpg. "
            f"Available indices: {list_clothes_items(category)['indices']}"
        )
    return _load_asset(asset_path, return_type)


def avatar(
    i: int = 1,
    *,
    return_type: ReturnType = "path",
) -> Path | bytes | "Image.Image":
    """Get an example avatar image.

    Args:
        i: Avatar index (default 1).
        return_type: How to return the asset - 'path' (default), 'pil', or 'bytes'.

    Returns:
        Path to avatar image, PIL Image, or bytes depending on return_type.

    Raises:
        FileNotFoundError: If the avatar doesn't exist.

    Example:
        >>> example.avatar(i=1)
        PosixPath('.../1.png')
    """
    assets_path = _get_assets_path()
    avatar_path = assets_path / "avatars" / f"{i}.png"

    if not avatar_path.exists():
        # List available avatars for helpful error message
        avatars_dir = assets_path / "avatars"
        if avatars_dir.exists():
            available = sorted(
                int(f.stem) for f in avatars_dir.glob("*.png") if f.stem.isdigit()
            )
        else:
            available = []

        raise FileNotFoundError(
            f"Avatar not found: {i}.png. Available avatars: {available or 'none'}"
        )

    return _load_asset(avatar_path, return_type)


def person(
    i: int = 1,
    kind: Literal["posture", "selfie"] = "posture",
    *,
    return_type: ReturnType = "path",
) -> Path | bytes | "Image.Image":
    """Get an example person photo.

    Args:
        i: Person index (default 1).
        kind: Type of photo - 'posture' (full body) or 'selfie' (face/upper body).
        return_type: How to return the asset - 'path' (default), 'pil', or 'bytes'.

    Returns:
        Path to person photo, PIL Image, or bytes depending on return_type.

    Raises:
        ValueError: If kind is invalid.
        FileNotFoundError: If the person photo doesn't exist.

    Example:
        >>> example.person(i=1, kind="posture")
        PosixPath('.../1_posture.jpg')
    """
    _validate_person_kind(kind)

    assets_path = _get_assets_path()
    person_path = assets_path / "people" / f"{i}_{kind}.jpg"

    if not person_path.exists():
        # List available people for helpful error message
        people_dir = assets_path / "people"
        if people_dir.exists():
            available_indices = sorted(
                {
                    int(f.stem.split("_")[0])
                    for f in people_dir.glob("*_*.jpg")
                    if f.stem.split("_")[0].isdigit()
                }
            )
        else:
            available_indices = []

        raise FileNotFoundError(
            f"Person photo not found: {i}_{kind}.jpg. "
            f"Available indices: {available_indices or 'none'}. "
            f"Available kinds: {', '.join(sorted(VALID_PERSON_KINDS))}"
        )

    return _load_asset(person_path, return_type)
