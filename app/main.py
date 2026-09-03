"""
FastAPI Main Application Entry Point

This is the main FastAPI application that serves the Kerykeion astrology API.
"""

import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import Settings, settings


SOURCE_REPOSITORY = "https://github.com/raydevkit/kerykeion"


def create_app(app_settings: Settings = settings) -> FastAPI:
    """Create the API for the supplied runtime settings."""
    production = app_settings.ENVIRONMENT == "production"
    application = FastAPI(
        title="Kerykeion Astrology API",
        description="A FastAPI microservice wrapping the Kerykeion astrology library for the Kabalah platform",
        version=app_settings.APP_VERSION,
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )
    application.state.settings = app_settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "version": app_settings.APP_VERSION,
            "environment": app_settings.ENVIRONMENT,
        }

    @application.get("/", tags=["Root"])
    async def root():
        source = SOURCE_REPOSITORY
        if re.fullmatch(r"[0-9a-fA-F]{40}", app_settings.GIT_REVISION):
            source = f"{SOURCE_REPOSITORY}/tree/{app_settings.GIT_REVISION}"
        payload = {
            "message": "Kerykeion Astrology API",
            "version": app_settings.APP_VERSION,
            "revision": app_settings.GIT_REVISION,
            "health": "/health",
            "source": source,
        }
        if not production:
            payload["docs"] = "/docs"
        return payload

    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=2 if settings.ENVIRONMENT == "production" else 1,
    )
