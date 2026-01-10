"""Example assets endpoints."""

from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from openvto import example

from app.models import ClothingCategoriesResponse, ClothingItemsResponse

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/clothes/categories", response_model=ClothingCategoriesResponse)
async def list_clothing_categories():
    """List available clothing categories."""
    return {"categories": example.list_clothes_categories()}


@router.get("/clothes/{category}", response_model=ClothingItemsResponse)
async def list_clothing_items(category: str):
    """List items in a clothing category."""
    try:
        items = example.list_clothes_items(category)
        return {"category": category, **items}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/clothes/{category}/{item_id}/{view}")
async def get_clothing_image(
    category: str,
    item_id: int,
    view: Literal["front", "back"],
):
    """Get a specific clothing image."""
    try:
        image_bytes = example.clothes(
            category, i=item_id, view=view, return_type="bytes"
        )
        return Response(content=image_bytes, media_type="image/jpeg")
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/people/{person_id}/{kind}")
async def get_person_image(
    person_id: int,
    kind: Literal["posture", "selfie"],
):
    """Get a person photo (posture or selfie)."""
    try:
        image_bytes = example.person(i=person_id, kind=kind, return_type="bytes")
        return Response(content=image_bytes, media_type="image/jpeg")
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/avatars/{avatar_id}")
async def get_avatar_image(avatar_id: int):
    """Get a pre-generated avatar image."""
    try:
        image_bytes = example.avatar(i=avatar_id, return_type="bytes")
        return Response(content=image_bytes, media_type="image/png")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
