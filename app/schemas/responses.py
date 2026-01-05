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


class SynastryDataResponse(BaseModel):
    """Data container for synastry chart response"""
    
    subject_one_chart: Dict[str, Any] = Field(..., description="Birth chart data for subject one")
    subject_two_chart: Dict[str, Any] = Field(..., description="Birth chart data for subject two")
    aspects: List[Dict[str, Any]] = Field(..., description="Synastry aspects between charts")


class SynastryChartResponse(BaseModel):
    """Response schema for synastry chart"""

    svg: Optional[str] = Field(None, description="Synastry chart SVG")
    data: SynastryDataResponse = Field(..., description="Synastry chart data with aspects")


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


class LunarPhaseData(BaseModel):
    """Lunar phase information"""
    
    name: str = Field(..., description="Name of the lunar phase (e.g., 'Waxing Crescent')")
    emoji: str = Field(..., description="Moon phase emoji")
    day: int = Field(..., description="Day of the lunar cycle (0-29)")
    illumination: float = Field(..., description="Percentage of moon illumination (0-100)")
    degrees_between_sun_moon: float = Field(..., description="Angular distance between Sun and Moon")


class MoonPhaseInfo(BaseModel):
    """Moon phase name and illumination"""
    
    name: str = Field(..., description="Phase name (e.g., 'Waxing Gibbous')")
    emoji: str = Field(..., description="Moon phase emoji")
    illumination: float = Field(..., description="Percentage illumination (0-100)")
    is_waxing: bool = Field(..., description="True if waxing, False if waning")


class MoonAgeInfo(BaseModel):
    """Moon age information"""
    
    days: float = Field(..., description="Moon age in days with decimal precision")
    phase_day: int = Field(..., description="Integer day of lunar cycle (0-29)")
    synodic_month: float = Field(..., description="Length of synodic month in days")
    percent_complete: float = Field(..., description="Percentage of lunar cycle complete")


class NextPhaseInfo(BaseModel):
    """Information about the next lunar phase"""
    
    name: str = Field(..., description="Name of the next major phase")
    days_until: float = Field(..., description="Days until next phase")


class MoonPositionInfo(BaseModel):
    """Moon's position in the zodiac"""
    
    sign: str = Field(..., description="Zodiac sign")
    sign_emoji: str = Field(..., description="Sign emoji")
    degree: float = Field(..., description="Position within sign (0-30)")
    abs_degree: float = Field(..., description="Absolute position (0-360)")
    element: str = Field(..., description="Element (Fire, Earth, Air, Water)")
    quality: str = Field(..., description="Quality (Cardinal, Fixed, Mutable)")


class SunPositionInfo(BaseModel):
    """Sun's position reference"""
    
    sign: str = Field(..., description="Zodiac sign")
    degree: float = Field(..., description="Position within sign")


class GeometryInfo(BaseModel):
    """Sun-Moon geometry"""
    
    elongation: float = Field(..., description="Angular distance between Sun and Moon")
    sun_phase: int = Field(..., description="Sun phase indicator")


class MoonPhaseResponse(BaseModel):
    """Response schema for detailed moon phase information"""
    
    timestamp: str = Field(..., description="Current timestamp (UTC)")
    location: Dict[str, Any] = Field(..., description="Location data")
    phase: MoonPhaseInfo = Field(..., description="Current phase information")
    age: MoonAgeInfo = Field(..., description="Moon age information")
    next_phase: NextPhaseInfo = Field(..., description="Next phase information")
    moon_position: MoonPositionInfo = Field(..., description="Moon's zodiac position")
    sun_position: SunPositionInfo = Field(..., description="Sun's zodiac position")
    geometry: GeometryInfo = Field(..., description="Sun-Moon geometry")


class CurrentSkyResponse(BaseModel):
    """Response schema for current planetary positions"""

    date: str = Field(..., description="Current date and time (UTC)")
    location: Dict[str, Any] = Field(..., description="Location data (longitude, latitude, timezone)")
    
    # Individual planets (matching birth chart format)
    sun: Dict[str, Any] = Field(..., description="Sun position data")
    moon: Dict[str, Any] = Field(..., description="Moon position data")
    mercury: Dict[str, Any] = Field(..., description="Mercury position data")
    venus: Dict[str, Any] = Field(..., description="Venus position data")
    mars: Dict[str, Any] = Field(..., description="Mars position data")
    jupiter: Dict[str, Any] = Field(..., description="Jupiter position data")
    saturn: Dict[str, Any] = Field(..., description="Saturn position data")
    uranus: Dict[str, Any] = Field(..., description="Uranus position data")
    neptune: Dict[str, Any] = Field(..., description="Neptune position data")
    pluto: Dict[str, Any] = Field(..., description="Pluto position data")
    
    # Houses and lunar phase
    houses: List[Dict[str, Any]] = Field(..., description="House cusps data")
    lunar_phase: Optional[LunarPhaseData] = Field(None, description="Current lunar phase information")


class HealthCheckResponse(BaseModel):
    """Response schema for health check"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Current environment")
