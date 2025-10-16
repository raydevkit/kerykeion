"""
API v1 Main Router

Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import birth_chart, synastry, transit, composite, relationship, sky

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(birth_chart.router, prefix="/birth", tags=["Birth Charts"])
api_router.include_router(synastry.router, prefix="/synastry", tags=["Synastry"])
api_router.include_router(transit.router, prefix="/transit", tags=["Transits"])
api_router.include_router(composite.router, prefix="/composite", tags=["Composite"])
api_router.include_router(relationship.router, prefix="/relationship", tags=["Relationship"])
api_router.include_router(sky.router, prefix="/sky", tags=["Current Sky"])
