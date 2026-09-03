"""
Application Configuration

Uses pydantic-settings to load configuration from environment variables.
"""

import re
from typing import List, Literal
from urllib.parse import urlsplit

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    API_KEY: str = "your-secret-api-key-change-this-in-production"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    APP_VERSION: str = "dev"
    GIT_REVISION: str = "unknown"

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

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, origins):
        for origin in origins:
            parsed = urlsplit(origin)
            if origin == "*" or parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("CORS_ORIGINS must contain explicit HTTP(S) origins")
        return origins

    @field_validator("GIT_REVISION")
    @classmethod
    def normalize_git_revision(cls, revision):
        if re.fullmatch(r"[0-9a-fA-F]{40}", revision):
            return revision.lower()
        return revision

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT == "production" and (
            self.API_KEY == "your-secret-api-key-change-this-in-production" or len(self.API_KEY) < 32
        ):
            raise ValueError("production API_KEY must be non-default and at least 32 characters")
        if self.ENVIRONMENT == "production" and not re.fullmatch(r"[0-9a-f]{40}", self.GIT_REVISION):
            raise ValueError("production GIT_REVISION must be a full 40-character Git SHA")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create global settings instance
settings = Settings()
