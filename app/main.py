"""
FastAPI Main Application Entry Point

This is the main FastAPI application that serves the Kerykeion astrology API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import Settings, settings


def create_app(app_settings: Settings = settings) -> FastAPI:
    """Create the API for the supplied runtime settings."""
    production = app_settings.ENVIRONMENT == "production"
    application = FastAPI(
        title="Kerykeion Astrology API",
        description="A FastAPI microservice wrapping the Kerykeion astrology library for the Kabalah platform",
        version="1.0.0",
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )
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
            "version": "1.0.0",
            "environment": app_settings.ENVIRONMENT,
        }

    @application.get("/", tags=["Root"])
    async def root():
        return {
            "message": "Kerykeion Astrology API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "source": "https://github.com/raydevkit/kerykeion/tree/chore/fast-api",
        }

    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
