from datetime import date, datetime, timedelta, timezone

from fastapi.testclient import TestClient
import pytest
import swisseph as swe

from app.core.config import settings
from app.main import app
from app.services.forecast_service import TROPICAL_YEAR_DAYS, progressed_moment

client = TestClient(app)
HEADERS = {"X-API-Key": settings.API_KEY}
SUBJECT = {
    "name": "Test",
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "longitude": 12.4964,
    "latitude": 41.9028,
    "timezone": "Europe/Rome",
    "city": "Rome",
    "nation": "IT",
}


def _julian(iso: str) -> float:
    moment = datetime.fromisoformat(iso).astimezone(timezone.utc)
    hours = moment.hour + moment.minute / 60 + (moment.second + moment.microsecond / 1e6) / 3600
    return swe.julday(moment.year, moment.month, moment.day, hours)


def _longitude(jd: float, body: int) -> float:
    return swe.calc_ut(jd, body)[0][0]


def _angle(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def test_solar_return_finds_the_moment_the_sun_is_back_on_its_natal_degree():
    response = client.post("/api/v1/return/solar", json={"subject": SUBJECT, "year": 2026}, headers=HEADERS)

    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    assert "<svg" in body["svg"][:500]
    assert data["return_moment_local"].startswith("2026-05-1")
    assert data["return_moment_local"].endswith("+02:00")
    natal_sun = data["natal_chart"]["sun"]["abs_pos"]
    # Independent check against the raw ephemeris: the Sun at the reported moment sits on the natal degree.
    assert _angle(_longitude(_julian(data["return_moment_utc"]), swe.SUN), natal_sun) < 1 / 60
    assert _angle(data["return_chart"]["sun"]["abs_pos"], natal_sun) < 1 / 3600
    assert data["return_chart"]["date"]["year"] == 2026
    assert data["return_chart"]["location"]["city"] == "Rome"
    assert data["aspects_to_natal"]


def test_solar_return_is_cast_for_the_given_location():
    tokyo = {"longitude": 139.6917, "latitude": 35.6895, "timezone": "Asia/Tokyo", "city": "Tokyo", "nation": "JP"}
    rome = client.post("/api/v1/return/solar", json={"subject": SUBJECT, "year": 2026}, headers=HEADERS).json()
    moved = client.post(
        "/api/v1/return/solar", json={"subject": SUBJECT, "year": 2026, "location": tokyo}, headers=HEADERS
    ).json()

    assert moved["data"]["return_moment_utc"] == rome["data"]["return_moment_utc"]
    assert moved["data"]["return_moment_local"].endswith("+09:00")
    assert moved["data"]["return_chart"]["location"]["city"] == "Tokyo"
    assert moved["data"]["return_chart"]["houses"][0]["abs_pos"] != rome["data"]["return_chart"]["houses"][0]["abs_pos"]


def test_solar_return_for_an_early_january_birthday_stays_in_the_requested_year():
    # Born on Jan 1 in Tokyo: the natal Sun crosses on Dec 31 UTC, so a search from Jan 1 UTC would skip a year.
    subject = {**SUBJECT, "month": 1, "day": 1, "hour": 3, "minute": 0, "longitude": 139.6917,
               "latitude": 35.6895, "timezone": "Asia/Tokyo", "city": "Tokyo", "nation": "JP"}

    data = client.post("/api/v1/return/solar", json={"subject": subject, "year": 2026}, headers=HEADERS).json()["data"]

    assert data["return_moment_local"][:4] in {"2025", "2026"}
    assert abs(datetime.fromisoformat(data["return_moment_local"]).date() - date(2026, 1, 1)) <= timedelta(days=1)


def test_progressed_moment_adds_one_day_per_year_lived():
    birth = datetime(1990, 5, 15, 12, 30, tzinfo=timezone.utc)

    assert progressed_moment(birth, date(1990, 5, 15)) == birth
    thirty = progressed_moment(birth, date(2020, 5, 15))
    assert abs((thirty - birth).total_seconds() / 86400 - 10958 / TROPICAL_YEAR_DAYS) < 1e-9
    with pytest.raises(ValueError):
        progressed_moment(birth, date(1990, 5, 14))


def test_progressions_return_progressed_positions_aspects_and_a_bi_wheel():
    response = client.post(
        "/api/v1/progressions", json={"subject": SUBJECT, "target_date": "2026-11-07"}, headers=HEADERS
    )

    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    assert "<svg" in body["svg"][:500]
    moment = datetime.fromisoformat(data["progressed_moment_utc"])
    birth = datetime(1990, 5, 15, 12, 30, tzinfo=timezone.utc)  # 14:30 in Rome, summer time
    assert 36 < (moment - birth).total_seconds() / 86400 < 37
    # The progressed Moon matches the raw ephemeris at the progressed moment.
    assert _angle(data["progressed_chart"]["moon"]["abs_pos"], _longitude(_julian(data["progressed_moment_utc"]), swe.MOON)) < 0.01
    assert data["natal_chart"]["sun"]["abs_pos"] != data["progressed_chart"]["sun"]["abs_pos"]
    assert data["aspects_to_natal"]


def test_progressions_refuse_a_target_before_birth():
    response = client.post(
        "/api/v1/progressions", json={"subject": SUBJECT, "target_date": "1980-01-01"}, headers=HEADERS
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_INPUT"


@pytest.mark.parametrize("path", ["/api/v1/return/solar", "/api/v1/progressions"])
def test_forecast_endpoints_need_the_api_key(path):
    assert client.post(path, json={}).status_code == 401
