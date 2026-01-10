"""Shared dependencies for the API."""

from fastapi import HTTPException

from openvto import OpenVTO

# Global VTO client instance
vto_client: OpenVTO | None = None


def get_vto_client() -> OpenVTO:
    """Get the VTO client, raising an error if not initialized."""
    if vto_client is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return vto_client
