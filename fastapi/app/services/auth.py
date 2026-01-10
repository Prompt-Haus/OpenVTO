"""Authentication service."""

import os

from fastapi import Header, HTTPException


def check_api_key(api_key: str = Header(...)) -> None:
    """Check if the API key provided in the request header is valid.

    Args:
        api_key: The API key provided in the request header.

    Raises:
        HTTPException: If the API key is invalid or missing.
    """
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        raise HTTPException(status_code=500, detail="API_KEY not configured")
    if api_key != expected_key:
        raise HTTPException(status_code=403, detail="Forbidden")
