"""Clothing image composer for combining multiple items."""

from __future__ import annotations

import io
from dataclasses import dataclass

from openvto.errors import ImageProcessingError
from openvto.types import ClothingItem, Outfit
from openvto.utils.images import load_image_bytes


@dataclass
class CompositeResult:
    """Result from clothing composition.

    Attributes:
        image: Composite image bytes.
        width: Image width.
        height: Image height.
        item_count: Number of items in composite.
        layout: Layout type used.
        description: Combined description of items.
    """

    image: bytes
    width: int
    height: int
    item_count: int
    layout: str
    description: str


def compose_clothing(
    items: list[ClothingItem] | Outfit,
    *,
    layout: str = "grid",
    max_width: int = 1024,
    max_height: int = 1024,
    padding: int = 20,
) -> CompositeResult:
    """Compose multiple clothing items into a single image.

    This optimizes token usage by sending one composite image instead of
    multiple separate images to the generation API.

    Args:
        items: List of ClothingItem or an Outfit.
        layout: Layout strategy ("grid", "horizontal", "vertical").
        max_width: Maximum output width.
        max_height: Maximum output height.
        padding: Padding between items in pixels.

    Returns:
        CompositeResult with composed image and metadata.

    Raises:
        ImageProcessingError: If composition fails.
    """
    # Normalize input
    if isinstance(items, Outfit):
        clothing_items = items.items
    else:
        clothing_items = items

    if not clothing_items:
        raise ImageProcessingError("No clothing items to compose")

    if len(clothing_items) == 1:
        # Single item - just load and return
        item = clothing_items[0]
        image_bytes = load_image_bytes(item.image)
        return CompositeResult(
            image=image_bytes,
            width=max_width,
            height=max_height,
            item_count=1,
            layout="single",
            description=_build_description([item]),
        )

    # Load all images
    try:
        from PIL import Image
    except ImportError:
        raise ImageProcessingError(
            "PIL/Pillow required for clothing composition. "
            "Install with: pip install Pillow"
        )

    images = []
    for item in clothing_items:
        img_bytes = load_image_bytes(item.image)
        img = Image.open(io.BytesIO(img_bytes))
        images.append(img)

    # Compose based on layout
    if layout == "horizontal":
        composite = _compose_horizontal(images, max_width, max_height, padding)
    elif layout == "vertical":
        composite = _compose_vertical(images, max_width, max_height, padding)
    else:  # grid
        composite = _compose_grid(images, max_width, max_height, padding)

    # Convert to bytes
    buffer = io.BytesIO()
    composite.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    return CompositeResult(
        image=image_bytes,
        width=composite.width,
        height=composite.height,
        item_count=len(clothing_items),
        layout=layout,
        description=_build_description(clothing_items),
    )


def _compose_grid(images: list, max_width: int, max_height: int, padding: int):
    """Compose images in a grid layout."""
    from PIL import Image

    n = len(images)
    cols = 2 if n <= 4 else 3
    rows = (n + cols - 1) // cols

    # Calculate cell size
    cell_width = (max_width - padding * (cols + 1)) // cols
    cell_height = (max_height - padding * (rows + 1)) // rows

    # Create canvas
    canvas = Image.new("RGBA", (max_width, max_height), (255, 255, 255, 255))

    for i, img in enumerate(images):
        row = i // cols
        col = i % cols

        # Resize to fit cell while maintaining aspect ratio
        img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)

        # Calculate position (centered in cell)
        x = padding + col * (cell_width + padding) + (cell_width - img.width) // 2
        y = padding + row * (cell_height + padding) + (cell_height - img.height) // 2

        # Handle RGBA/RGB conversion
        if img.mode == "RGBA":
            canvas.paste(img, (x, y), img)
        else:
            canvas.paste(img, (x, y))

    return canvas.convert("RGB")


def _compose_horizontal(images: list, max_width: int, max_height: int, padding: int):
    """Compose images horizontally."""
    from PIL import Image

    n = len(images)
    cell_width = (max_width - padding * (n + 1)) // n

    # Resize all images
    resized = []
    for img in images:
        img.thumbnail((cell_width, max_height - 2 * padding), Image.Resampling.LANCZOS)
        resized.append(img)

    # Find max height
    total_height = max(img.height for img in resized) + 2 * padding

    # Create canvas
    canvas = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 255))

    x = padding
    for img in resized:
        y = (total_height - img.height) // 2
        if img.mode == "RGBA":
            canvas.paste(img, (x, y), img)
        else:
            canvas.paste(img, (x, y))
        x += cell_width + padding

    return canvas.convert("RGB")


def _compose_vertical(images: list, max_width: int, max_height: int, padding: int):
    """Compose images vertically."""
    from PIL import Image

    n = len(images)
    cell_height = (max_height - padding * (n + 1)) // n

    # Resize all images
    resized = []
    for img in images:
        img.thumbnail((max_width - 2 * padding, cell_height), Image.Resampling.LANCZOS)
        resized.append(img)

    # Create canvas
    canvas = Image.new("RGBA", (max_width, max_height), (255, 255, 255, 255))

    y = padding
    for img in resized:
        x = (max_width - img.width) // 2
        if img.mode == "RGBA":
            canvas.paste(img, (x, y), img)
        else:
            canvas.paste(img, (x, y))
        y += cell_height + padding

    return canvas.convert("RGB")


def _build_description(items: list[ClothingItem]) -> str:
    """Build a text description of clothing items."""
    descriptions = []
    for item in items:
        parts = []
        if item.name:
            parts.append(item.name)
        if item.description:
            parts.append(item.description)
        if item.styling:
            parts.append(f"({item.styling})")
        if item.category:
            parts.append(f"[{item.category}]")

        if parts:
            descriptions.append(" ".join(parts))
        else:
            descriptions.append(f"clothing item {item.id}")

    return ", ".join(descriptions)
