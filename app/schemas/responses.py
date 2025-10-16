"""
Response Schemas

Pydantic models for API response payloads.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PlanetData(BaseModel):
    """Planet information"""

    name: str
    sign: str
    position: float
    house: Optional[int] = None
    retrograde: bool
    element: Optional[str] = None
    quality: Optional[str] = None


class HouseData(BaseModel):
    """House information"""

    name: str
    sign: str
    position: float


class AspectData(BaseModel):
    """Aspect information between planets"""

    planet1: str
    planet2: str
    aspect: str
    angle: float
    orb: float


class BirthChartResponse(BaseModel):
    """Response schema for birth chart with SVG"""

    svg: Optional[str] = Field(None, description="SVG chart content")
    data: Dict[str, Any] = Field(..., description="Chart data")


class BirthDataResponse(BaseModel):
    """Response schema for birth chart data only (no SVG)"""

    name: str
    sun: Dict[str, Any]
    moon: Dict[str, Any]
    planets: List[Dict[str, Any]]
    houses: List[Dict[str, Any]]
    aspects: List[Dict[str, Any]]


class SynastryChartResponse(BaseModel):
    """Response schema for synastry chart"""

    svg: Optional[str] = Field(None, description="Synastry chart SVG")
    aspects: List[Dict[str, Any]] = Field(..., description="Aspects between charts")


class TransitChartResponse(BaseModel):
    """Response schema for transit chart"""

    svg: Optional[str] = Field(None, description="Transit chart SVG")
    transit_aspects: List[Dict[str, Any]] = Field(..., description="Transit aspects")


class CompositeChartResponse(BaseModel):
    """Response schema for composite chart"""

    svg: Optional[str] = Field(None, description="Composite chart SVG")
    composite_data: Dict[str, Any] = Field(..., description="Composite chart data")


class RelationshipScoreResponse(BaseModel):
    """Response schema for relationship compatibility score"""

    score: int = Field(..., description="Compatibility score")
    max_score: int = Field(..., description="Maximum possible score")
    percentage: float = Field(..., description="Compatibility percentage")
    rating: str = Field(..., description="Compatibility rating description")
    breakdown: Dict[str, int] = Field(..., description="Score breakdown by category")


class CurrentSkyResponse(BaseModel):
    """Response schema for current planetary positions"""

    date: str = Field(..., description="Current date and time (UTC)")
    planets: Dict[str, Dict[str, Any]] = Field(..., description="Current planetary positions")


class HealthCheckResponse(BaseModel):
    """Response schema for health check"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Current environment")
