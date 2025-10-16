"""
FastAPI Main Application Entry Point

This is the main FastAPI application that serves the Kerykeion astrology API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router

# Create FastAPI application
app = FastAPI(
    title="Kerykeion Astrology API",
    description="A FastAPI microservice wrapping the Kerykeion astrology library for the Kabalah platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify service status"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
        }
    )


# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return JSONResponse(
        content={
            "message": "Kerykeion Astrology API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
