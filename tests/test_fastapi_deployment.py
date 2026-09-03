from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from unittest.mock import patch

from app.core.config import Settings, settings
from app.main import app, create_app


def test_health_is_public():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_advertises_the_agpl_source():
    response = TestClient(app).get("/")

    assert response.json()["source"] == "https://github.com/raydevkit/kerykeion/tree/chore/fast-api"


def test_documentation_is_available_outside_production():
    client = TestClient(app)

    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_documentation_is_disabled_in_production():
    production = Settings(ENVIRONMENT="production", API_KEY="x" * 32, _env_file=None)
    client = TestClient(create_app(production))

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_production_rejects_the_default_api_key():
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="production", _env_file=None)


def test_production_rejects_a_short_api_key():
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="production", API_KEY="too-short", _env_file=None)


def test_cors_origins_are_parsed_from_a_comma_separated_value():
    config = Settings(CORS_ORIGINS="https://kabalah.example, http://localhost:3000", _env_file=None)

    assert config.CORS_ORIGINS == ["https://kabalah.example", "http://localhost:3000"]


@pytest.mark.parametrize("origins", ["*", "ftp://kabalah.example", ""])
def test_cors_origins_reject_wildcards_and_invalid_urls(origins):
    with pytest.raises(ValidationError):
        Settings(CORS_ORIGINS=origins, _env_file=None)


def test_protected_endpoint_rejects_a_missing_api_key():
    response = TestClient(app).get("/api/v1/sky/now")

    assert response.status_code == 401


def test_protected_endpoint_rejects_an_invalid_api_key():
    response = TestClient(app).get("/api/v1/sky/now", headers={"X-API-Key": "wrong"})

    assert response.status_code == 403


def test_protected_endpoint_accepts_the_configured_api_key():
    sky = {
        "date": "2026-01-01T00:00:00Z",
        "location": {},
        **{name: {} for name in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")},
        "houses": [],
        "lunar_phase": None,
    }

    with patch("app.api.v1.sky.get_current_sky_positions", return_value=sky):
        response = TestClient(app).get("/api/v1/sky/now", headers={"X-API-Key": settings.API_KEY})

    assert response.status_code == 200


def test_internal_errors_do_not_leak_exception_messages():
    with patch("app.api.v1.sky.get_current_sky_positions", side_effect=RuntimeError("private-token-123")):
        response = TestClient(app, raise_server_exceptions=False).get(
            "/api/v1/sky/now", headers={"X-API-Key": settings.API_KEY}
        )

    assert response.status_code == 500
    assert "private-token-123" not in response.text
