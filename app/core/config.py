"""
Application Configuration

Uses pydantic-settings to load configuration from environment variables.
"""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    API_KEY: str = "your-secret-api-key-change-this-in-production"
    ENVIRONMENT: str = "development"

    # CORS Configuration
    CORS_ORIGINS: str | List[str] = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Kerykeion Configuration
    DEFAULT_ZODIAC_TYPE: str = "Tropic"
    DEFAULT_HOUSE_SYSTEM: str = "P"  # P=Placidus
    DEFAULT_CHART_THEME: str = "light"
    DEFAULT_CHART_LANGUAGE: str = "EN"

    # GeoNames API Configuration
    GEONAMES_USERNAME: str = "geonames_demo"  # Default fallback

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create global settings instance
settings = Settings()
