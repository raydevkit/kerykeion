"""
API Security and Authentication

Handles API key validation for securing endpoints.
"""

import secrets

from fastapi import HTTPException, Request, Security, status
from fastapi.security.api_key import APIKeyHeader

from app.core.config import Settings

# API Key header configuration
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(request: Request, api_key: str | None = Security(api_key_header)) -> str:
    """
    Verify the API key from the request header.

    Args:
        api_key: The API key from the X-API-Key header

    Returns:
        str: The verified API key

    Raises:
        HTTPException: If the API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Please provide X-API-Key header.",
        )

    app_settings: Settings = request.app.state.settings
    if not secrets.compare_digest(api_key, app_settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key. Access denied.",
        )

    return api_key
