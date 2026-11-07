"""
Request Schemas

Pydantic models for API request payloads.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field
from app.schemas.common import SubjectInput, ChartConfig


class BirthChartRequest(BaseModel):
    """Request schema for birth chart generation"""

    subject: SubjectInput
    config: ChartConfig = Field(default_factory=ChartConfig)

    class Config:
        json_schema_extra = {
            "example": {
                "subject": {
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
                },
                "config": {
                    "zodiac_type": "Tropic",
                    "house_system": "Placidus",
                    "theme": "light",
                    "language": "EN"
                }
            }
        }


class SynastryRequest(BaseModel):
    """Request schema for synastry chart generation"""

    subject_one: SubjectInput = Field(..., description="First person's birth data")
    subject_two: SubjectInput = Field(..., description="Second person's birth data")
    config: ChartConfig = Field(default_factory=ChartConfig)

    class Config:
        json_schema_extra = {
            "example": {
                "subject_one": {
                    "name": "Person A",
                    "year": 1990,
                    "month": 5,
                    "day": 15,
                    "hour": 14,
                    "minute": 30,
                    "longitude": -74.006,
                    "latitude": 40.7128,
                    "timezone": "America/New_York",
                    "city": "New York"
                },
                "subject_two": {
                    "name": "Person B",
                    "year": 1992,
                    "month": 8,
                    "day": 20,
                    "hour": 10,
                    "minute": 15,
                    "longitude": -118.15,
                    "latitude": 34.03,
                    "timezone": "America/Los_Angeles",
                    "city": "Los Angeles"
                },
                "config": {
                    "theme": "light",
                    "language": "EN"
                }
            }
        }


class TransitRequest(BaseModel):
    """Request schema for transit chart generation"""

    subject: SubjectInput = Field(..., description="Natal chart subject")
    transit_date: SubjectInput = Field(..., description="Transit date and time")
    config: ChartConfig = Field(default_factory=ChartConfig)


class CompositeRequest(BaseModel):
    """Request schema for composite chart generation"""

    subject_one: SubjectInput = Field(..., description="First person's birth data")
    subject_two: SubjectInput = Field(..., description="Second person's birth data")
    config: ChartConfig = Field(default_factory=ChartConfig)


class ReturnLocation(BaseModel):
    """Where the solar return is cast; defaults to the birth place."""

    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    timezone: str = Field(..., description="Timezone string (e.g., 'Europe/Rome')")
    city: Optional[str] = None
    nation: Optional[str] = None


class SolarReturnRequest(BaseModel):
    """Request schema for a solar return chart"""

    subject: SubjectInput = Field(..., description="Natal chart subject")
    year: int = Field(..., ge=1800, le=2100, description="Calendar year of the birthday to cast")
    location: Optional[ReturnLocation] = Field(None, description="Return location; the birth place when omitted")
    config: ChartConfig = Field(default_factory=ChartConfig)


class ProgressionsRequest(BaseModel):
    """Request schema for secondary progressions (a day for a year)"""

    subject: SubjectInput = Field(..., description="Natal chart subject")
    target_date: date = Field(..., description="The date to progress to (YYYY-MM-DD)")
    config: ChartConfig = Field(default_factory=ChartConfig)
