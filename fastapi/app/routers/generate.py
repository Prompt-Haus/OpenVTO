"""Generation endpoints."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from openvto import OpenVTO

from app.dependencies import get_vto_client
from app.models import AvatarResponse, TryOnResponse, VideoLoopResponse
from app.utils import bytes_to_b64, meta_to_response

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("/avatar", response_model=AvatarResponse)
async def generate_avatar(
    selfie: UploadFile = File(..., description="Selfie/face image"),
    posture: UploadFile = File(..., description="Full-body posture image"),
    background: str = Form("studio"),
    keep_clothes: bool = Form(False),
    seed: int | None = Form(None),
    vto: OpenVTO = Depends(get_vto_client),
):
    """Generate a studio-quality avatar from selfie and posture images."""
    selfie_bytes = await selfie.read()
    posture_bytes = await posture.read()

    result = vto.generate_avatar(
        selfie=selfie_bytes,
        posture=posture_bytes,
        background=background,
        keep_clothes=keep_clothes,
        seed=seed,
    )

    return AvatarResponse(
        image_b64=bytes_to_b64(result.image),
        width=result.avatar.width,
        height=result.avatar.height,
        meta=meta_to_response(result.meta),
    )


@router.post("/tryon", response_model=TryOnResponse)
async def generate_tryon(
    avatar: UploadFile = File(..., description="Avatar or base image"),
    clothes: list[UploadFile] = File(..., description="Clothing images"),
    compose: bool = Form(True),
    seed: int | None = Form(None),
    vto: OpenVTO = Depends(get_vto_client),
):
    """Generate virtual try-on with clothing on avatar."""
    avatar_bytes = await avatar.read()
    clothes_bytes = [await c.read() for c in clothes]

    result = vto.generate_tryon(
        avatar=avatar_bytes,
        clothes=clothes_bytes,
        compose=compose,
        seed=seed,
    )

    return TryOnResponse(
        image_b64=bytes_to_b64(result.image),
        clothing_composite_b64=(
            bytes_to_b64(result.clothing_composite)
            if result.clothing_composite
            else None
        ),
        meta=meta_to_response(result.meta),
    )


@router.post("/videoloop", response_model=VideoLoopResponse)
async def generate_videoloop(
    image: UploadFile = File(..., description="Static image to animate"),
    mode: str = Form("360"),
    seconds: float = Form(4.0, ge=4.0, le=8.0),
    seed: int | None = Form(None),
    vto: OpenVTO = Depends(get_vto_client),
):
    """Generate an animated video loop from a static image."""
    image_bytes = await image.read()

    result = vto.generate_videoloop(
        static_image=image_bytes,
        mode=mode,
        seconds=seconds,
        seed=seed,
    )

    return VideoLoopResponse(
        video_b64=bytes_to_b64(result.video),
        first_frame_b64=bytes_to_b64(result.first_frame),
        duration_seconds=result.duration_seconds,
        width=result.width,
        height=result.height,
        mode=result.mode.value,
        meta=meta_to_response(result.meta),
    )
