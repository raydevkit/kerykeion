"""
Request Schemas

Pydantic models for API request payloads.
"""

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
