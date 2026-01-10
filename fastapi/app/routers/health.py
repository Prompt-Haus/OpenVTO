"""Health check endpoints."""

from fastapi import APIRouter

import openvto

import os
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


@router.get("/env_vars", response_model=HealthResponse)
async def env_vars():
    """Environment variables endpoint."""
    return os.environ
