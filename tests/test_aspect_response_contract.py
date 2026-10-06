"""Exercise the real chart calculations and API aspect payloads without GeoNames."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.schemas.common import SubjectInput
from app.services.calculation_service import calculate_aspect_statistics
from app.services.kerykeion_service import create_astrological_subject, extract_aspect_data, get_synastry_aspects
from app.services.relationship_service import calculate_relationship_score, get_key_synastry_aspects


LISBON = {
    "name": "Lisbon",
    "year": 1992,
    "month": 5,
    "day": 14,
    "hour": 8,
    "minute": 30,
    "longitude": -9.1393,
    "latitude": 38.7223,
    "timezone": "Europe/Lisbon",
    "city": "Lisbon",
    "nation": "PT",
}
PARTNER = {**LISBON, "name": "Partner", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0}
TRANSIT = {**LISBON, "name": "Transit", "year": 2026, "month": 10, "day": 6, "hour": 12, "minute": 0}
MAJOR_ASPECTS = {"Conjunction", "Opposition", "Trine", "Square", "Sextile"}
ASPECT_KEYS = {"planet1", "planet2", "aspect", "angle", "orb"}
NATAL_KEYS = ASPECT_KEYS | {"is_active"}
DUAL_KEYS = ASPECT_KEYS | {"planet1_owner", "planet2_owner", "color"}


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("Aspect contract tests must not make external requests")

    monkeypatch.setattr("kerykeion.fetch_geonames.FetchGeonames.__init__", fail)
    monkeypatch.setattr("requests.sessions.Session.request", fail)
    monkeypatch.setattr("httpx.HTTPTransport.handle_request", fail)


@pytest.fixture
def client():
    config = Settings(ENVIRONMENT="test", API_KEY="aspect-contract-test", _env_file=None)
    with TestClient(create_app(config), headers={"X-API-Key": config.API_KEY}) as test_client:
        yield test_client


def assert_aspects(aspects, expected_keys):
    assert aspects
    assert any(aspect["aspect"] in MAJOR_ASPECTS for aspect in aspects)
    for aspect in aspects:
        assert set(aspect) == expected_keys
        assert aspect["planet1"] and aspect["planet2"]
        assert aspect["aspect"] == aspect["aspect"].capitalize()
        assert isinstance(aspect["angle"], (int, float))
        assert isinstance(aspect["orb"], (int, float))
        assert aspect["orb"] >= 0
        if "is_active" in expected_keys:
            assert aspect["is_active"] is True


@pytest.mark.parametrize("mode", ["chart", "data"])
def test_birth_aspects(client, mode):
    response = client.post(f"/api/v1/birth/{mode}", json={"subject": LISBON})
    assert response.status_code == 200, response.text
    data = response.json()
    if mode == "chart":
        assert "<svg" in data["svg"]
        data = data["data"]
    assert_aspects(data["aspects"], NATAL_KEYS)


@pytest.mark.parametrize("mode", ["chart", "data"])
def test_synastry_aspects(client, mode):
    response = client.post(
        f"/api/v1/synastry/{mode}", json={"subject_one": LISBON, "subject_two": PARTNER}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if mode == "chart":
        assert "<svg" in data["svg"]
        data = data["data"]
        for name in ("subject_one_chart", "subject_two_chart"):
            assert_aspects(data[name]["aspects"], NATAL_KEYS)
    else:
        assert data["aspect_count"] == len(data["aspects"])
    assert_aspects(data["aspects"], DUAL_KEYS)
    assert all(a["planet1_owner"] == "Lisbon" and a["planet2_owner"] == "Partner" for a in data["aspects"])


@pytest.mark.parametrize("mode", ["chart", "data"])
def test_transit_aspects(client, mode):
    response = client.post(
        f"/api/v1/transit/{mode}", json={"subject": LISBON, "transit_date": TRANSIT}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if mode == "chart":
        assert "<svg" in data["svg"]
    else:
        assert data["aspect_count"] == len(data["transit_aspects"])
    assert_aspects(data["transit_aspects"], DUAL_KEYS)
    assert all(a["planet1_owner"] == "Lisbon" and a["planet2_owner"] == "Transit" for a in data["transit_aspects"])


@pytest.mark.parametrize("mode", ["chart", "data"])
def test_composite_aspects(client, mode):
    response = client.post(
        f"/api/v1/composite/{mode}", json={"subject_one": LISBON, "subject_two": PARTNER}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if mode == "chart":
        assert "<svg" in data["svg"]
    assert_aspects(data["composite_data"]["aspects"], NATAL_KEYS)


def test_natal_aspect_values_and_statistics():
    subject = create_astrological_subject(SubjectInput(**LISBON))
    aspects = extract_aspect_data(subject)
    assert_aspects(aspects, NATAL_KEYS)
    # Check the mapping against the planets' actual angular separation.
    conjunction = next(
        a for a in aspects if a["planet1"] == "Uranus" and a["planet2"] == "Neptune"
    )
    assert conjunction["aspect"] == "Conjunction"
    assert conjunction["angle"] == 0
    assert conjunction["orb"] == pytest.approx(abs(subject.uranus.abs_pos - subject.neptune.abs_pos))
    assert conjunction["is_active"] is True
    statistics = calculate_aspect_statistics(subject)
    assert statistics["aspects"] == aspects
    assert statistics["total_aspects"] == sum(statistics["aspect_breakdown"].values()) == len(aspects)
    assert set(statistics["aspect_breakdown"]) == {a["aspect"] for a in aspects}


def test_relationship_uses_populated_aspects_without_changing_score(client, monkeypatch):
    first = create_astrological_subject(SubjectInput(**LISBON))
    second = create_astrological_subject(SubjectInput(**PARTNER))
    aspects = get_synastry_aspects(first, second)
    assert_aspects(aspects, DUAL_KEYS)
    assert_aspects(get_key_synastry_aspects(first, second), DUAL_KEYS | {"importance"})
    score = calculate_relationship_score(first, second)
    assert score["aspect_count"] == len(aspects)
    response = client.post("/api/v1/relationship/score", json={"subject_one": LISBON, "subject_two": PARTNER})
    assert response.status_code == 200, response.text
    assert response.json()["percentage"] == score["percentage"]
    assert response.json()["breakdown"] == score["breakdown"]
    lowercase_aspects = [{**a, "aspect": a["aspect"].lower()} for a in aspects]
    monkeypatch.setattr("app.services.relationship_service.get_synastry_aspects", lambda *args: lowercase_aspects)
    assert calculate_relationship_score(first, second) == score
