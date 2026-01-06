"""Generation pipelines for avatar, try-on, and video loop creation."""

from openvto.pipelines.avatar import generate_avatar
from openvto.pipelines.composer import CompositeResult, compose_clothing
from openvto.pipelines.tryon import generate_tryon
from openvto.pipelines.videoloop import generate_videoloop

__all__ = [
    "CompositeResult",
    "compose_clothing",
    "generate_avatar",
    "generate_tryon",
    "generate_videoloop",
]
