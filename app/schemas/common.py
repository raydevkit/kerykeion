"""
Common Pydantic Schemas

Shared schemas used across multiple endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


class SubjectInput(BaseModel):
    """Input schema for astrological subject (birth data)"""

    name: str = Field(..., description="Subject's name")
    year: int = Field(..., ge=1800, le=2100, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Birth day (1-31)")
    hour: int = Field(..., ge=0, le=23, description="Birth hour (0-23)")
    minute: int = Field(..., ge=0, le=59, description="Birth minute (0-59)")

    # Location - either city/nation OR lng/lat/timezone
    city: Optional[str] = Field(None, description="Birth city name")
    nation: Optional[str] = Field(None, description="Birth nation code (e.g., 'US')")

    # Or provide coordinates directly (recommended for offline mode)
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    timezone: Optional[str] = Field(None, description="Timezone string (e.g., 'America/New_York')")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "year": 1990,
                "month": 5,
                "day": 15,
                "hour": 14,
                "minute": 30,
                "longitude": -74.006,
                "latitude": 40.7128,
                "timezone": "America/New_York",
                "city": "New York"
            }
        }


class ChartConfig(BaseModel):
    """Configuration for chart generation"""

    zodiac_type: str = Field(
        default="Tropic",
        description="Zodiac type: 'Tropic'/'Tropical' (Western) or 'Sidereal'/'Vedic'"
    )
    sidereal_mode: Optional[str] = Field(
        default=None,
        description="Sidereal mode (e.g., 'LAHIRI'). Only used when zodiac_type='Sidereal'"
    )
    house_system: str = Field(
        default="P",
        description="House system: Use full name (e.g., 'Placidus', 'Koch', 'Whole Sign') or code (P, K, W, E, C, R, O, M). Common systems: Placidus (P), Koch (K), Whole Sign (W), Equal (E), Campanus (C), Regiomontanus (R), Porphyrius (O), Morinus (M)"
    )
    theme: str = Field(
        default="light",
        description="Chart theme: 'light', 'dark', 'classic', 'dark_high_contrast'"
    )
    language: str = Field(
        default="EN",
        description="Chart language: EN, ES, FR, PT, IT, DE, RU, TR, CN, HI"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "zodiac_type": "Tropic",
                "house_system": "Placidus",
                "theme": "light",
                "language": "EN"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: dict = Field(..., description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Invalid birth date provided",
                    "details": {}
                }
            }
        }
