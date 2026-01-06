"""Image processing utilities for OpenVTO."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from openvto.errors import ImageProcessingError, ValidationError

if TYPE_CHECKING:
    pass

# Default dimensions (9:16 aspect ratio for fashion/portrait)
DEFAULT_WIDTH = 720
DEFAULT_HEIGHT = 1280


def load_image_bytes(source: str | Path | bytes | BinaryIO) -> bytes:
    """Load image from various sources into bytes.

    Args:
        source: Image source - can be:
            - str: File path or URL
            - Path: File path
            - bytes: Raw image bytes
            - BinaryIO: File-like object

    Returns:
        Image as bytes.

    Raises:
        ValidationError: If source type is not supported.
        ImageProcessingError: If image cannot be loaded.
    """
    if isinstance(source, bytes):
        return source

    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists():
            try:
                return path.read_bytes()
            except OSError as e:
                raise ImageProcessingError(f"Failed to read image file: {e}")

        # Check if it's a URL
        source_str = str(source)
        if source_str.startswith(("http://", "https://")):
            return _fetch_image_url(source_str)

        raise ValidationError(f"Image file not found: {source}")

    if hasattr(source, "read"):
        try:
            return source.read()
        except OSError as e:
            raise ImageProcessingError(f"Failed to read image from stream: {e}")

    # Try PIL Image
    try:
        from PIL import Image

        if isinstance(source, Image.Image):
            return pil_to_bytes(source)
    except ImportError:
        pass

    raise ValidationError(
        f"Unsupported image source type: {type(source).__name__}. "
        "Expected: str, Path, bytes, BinaryIO, or PIL.Image"
    )


def _fetch_image_url(url: str) -> bytes:
    """Fetch image from URL.

    Args:
        url: Image URL.

    Returns:
        Image bytes.

    Raises:
        ImageProcessingError: If fetch fails.
    """
    try:
        import urllib.request

        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except Exception as e:
        raise ImageProcessingError(f"Failed to fetch image from URL: {e}")


def pil_to_bytes(image, format: str = "PNG") -> bytes:
    """Convert PIL Image to bytes.

    Args:
        image: PIL Image object.
        format: Output format (PNG, JPEG, WEBP).

    Returns:
        Image as bytes.
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def bytes_to_pil(image_bytes: bytes):
    """Convert bytes to PIL Image.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        PIL Image object.

    Raises:
        ImageProcessingError: If PIL is not installed or image is invalid.
    """
    try:
        from PIL import Image

        return Image.open(io.BytesIO(image_bytes))
    except ImportError:
        raise ImageProcessingError(
            "PIL/Pillow is required for image processing. "
            "Install with: pip install Pillow"
        )
    except Exception as e:
        raise ImageProcessingError(f"Failed to parse image: {e}")


def encode_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Base64 encoded string.
    """
    return base64.b64encode(image_bytes).decode("utf-8")


def decode_base64(base64_string: str) -> bytes:
    """Decode base64 string to image bytes.

    Args:
        base64_string: Base64 encoded string.

    Returns:
        Raw image bytes.
    """
    return base64.b64decode(base64_string)


def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """Get image dimensions without fully loading the image.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Tuple of (width, height).

    Raises:
        ImageProcessingError: If dimensions cannot be determined.
    """
    try:
        from PIL import Image

        with Image.open(io.BytesIO(image_bytes)) as img:
            return img.size
    except ImportError:
        # Fallback: try to parse PNG/JPEG headers manually
        return _parse_image_dimensions(image_bytes)
    except Exception as e:
        raise ImageProcessingError(f"Failed to get image dimensions: {e}")


def _parse_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """Parse image dimensions from file headers (PNG/JPEG only)."""
    import struct

    # PNG
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        if len(image_bytes) >= 24:
            width, height = struct.unpack(">II", image_bytes[16:24])
            return width, height

    # JPEG
    if image_bytes[:2] == b"\xff\xd8":
        idx = 2
        while idx < len(image_bytes) - 8:
            if image_bytes[idx] != 0xFF:
                break
            marker = image_bytes[idx + 1]
            if marker in (0xC0, 0xC2):  # SOF0 or SOF2
                height, width = struct.unpack(">HH", image_bytes[idx + 5 : idx + 9])
                return width, height
            length = struct.unpack(">H", image_bytes[idx + 2 : idx + 4])[0]
            idx += 2 + length

    raise ImageProcessingError("Cannot determine image dimensions from headers")


def resize_image(
    image_bytes: bytes,
    width: int | None = None,
    height: int | None = None,
    *,
    maintain_aspect: bool = True,
    max_dimension: int | None = None,
) -> bytes:
    """Resize image to specified dimensions.

    Args:
        image_bytes: Input image bytes.
        width: Target width (optional).
        height: Target height (optional).
        maintain_aspect: Whether to maintain aspect ratio.
        max_dimension: Maximum dimension for either side.

    Returns:
        Resized image bytes.

    Raises:
        ImageProcessingError: If resize fails.
    """
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes))
        original_format = img.format or "PNG"

        if max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        elif width and height:
            if maintain_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
        elif width:
            ratio = width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((width, new_height), Image.Resampling.LANCZOS)
        elif height:
            ratio = height / img.height
            new_width = int(img.width * ratio)
            img = img.resize((new_width, height), Image.Resampling.LANCZOS)

        return pil_to_bytes(img, format=original_format)
    except ImportError:
        raise ImageProcessingError(
            "PIL/Pillow is required for image resizing. "
            "Install with: pip install Pillow"
        )
    except Exception as e:
        raise ImageProcessingError(f"Failed to resize image: {e}")


def crop_to_aspect_ratio(
    image_bytes: bytes,
    aspect_width: int = 9,
    aspect_height: int = 16,
    *,
    position: str = "center",
) -> bytes:
    """Crop image to specified aspect ratio.

    Args:
        image_bytes: Input image bytes.
        aspect_width: Aspect ratio width component.
        aspect_height: Aspect ratio height component.
        position: Crop position ("center", "top", "bottom").

    Returns:
        Cropped image bytes.

    Raises:
        ImageProcessingError: If crop fails.
    """
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes))
        original_format = img.format or "PNG"

        target_ratio = aspect_width / aspect_height
        current_ratio = img.width / img.height

        if abs(current_ratio - target_ratio) < 0.01:
            return image_bytes  # Already at target ratio

        if current_ratio > target_ratio:
            # Image is too wide, crop width
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            box = (left, 0, left + new_width, img.height)
        else:
            # Image is too tall, crop height
            new_height = int(img.width / target_ratio)
            if position == "top":
                top = 0
            elif position == "bottom":
                top = img.height - new_height
            else:  # center
                top = (img.height - new_height) // 2
            box = (0, top, img.width, top + new_height)

        img = img.crop(box)
        return pil_to_bytes(img, format=original_format)
    except ImportError:
        raise ImageProcessingError(
            "PIL/Pillow is required for image cropping. "
            "Install with: pip install Pillow"
        )
    except Exception as e:
        raise ImageProcessingError(f"Failed to crop image: {e}")


def normalize_for_generation(
    image_bytes: bytes,
    *,
    target_width: int = DEFAULT_WIDTH,
    target_height: int = DEFAULT_HEIGHT,
) -> bytes:
    """Normalize image for generation (crop + resize to standard dimensions).

    Args:
        image_bytes: Input image bytes.
        target_width: Target width.
        target_height: Target height.

    Returns:
        Normalized image bytes.
    """
    # First crop to target aspect ratio
    cropped = crop_to_aspect_ratio(
        image_bytes,
        aspect_width=target_width,
        aspect_height=target_height,
    )

    # Then resize to exact dimensions
    return resize_image(
        cropped, width=target_width, height=target_height, maintain_aspect=False
    )


def get_image_format(image_bytes: bytes) -> str:
    """Detect image format from bytes.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Format string ("PNG", "JPEG", "WEBP", "GIF", or "UNKNOWN").
    """
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if image_bytes[:2] == b"\xff\xd8":
        return "JPEG"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "WEBP"
    if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "GIF"
    return "UNKNOWN"


def convert_format(image_bytes: bytes, target_format: str = "PNG") -> bytes:
    """Convert image to different format.

    Args:
        image_bytes: Input image bytes.
        target_format: Target format ("PNG", "JPEG", "WEBP").

    Returns:
        Converted image bytes.
    """
    img = bytes_to_pil(image_bytes)

    # Handle RGBA to RGB conversion for JPEG
    if target_format.upper() == "JPEG" and img.mode == "RGBA":
        background = img.__class__.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background

    return pil_to_bytes(img, format=target_format)
