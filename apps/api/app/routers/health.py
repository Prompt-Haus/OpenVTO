"""Health check endpoints."""


import openvto
from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return {"status": "ok", "version": openvto.__version__}


@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": openvto.__version__}
