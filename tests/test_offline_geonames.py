import json
from pathlib import Path
import socket

import pytest
from requests import Request, Response

from kerykeion.fetch_geonames import FetchGeonames


RECORDINGS = sorted((Path(__file__).parent / "fixtures" / "geonames").glob("*.json"))


@pytest.mark.parametrize("path", RECORDINGS, ids=lambda path: path.stem)
def test_recorded_location_runs_through_geonames_parser(path):
    recording = json.loads(path.read_text(encoding="utf-8"))
    query = recording["query"]
    # The username must never determine whether a request can be served offline.
    fetch = FetchGeonames(query["q"], query["country"], username="unused-test-account")
    data = fetch.get_serialized_data()

    assert data == {
        **{key: recording["search"]["geonames"][0][key] for key in ("name", "lat", "lng", "countryCode")},
        "timezonestr": recording["timezone"]["timezoneId"],
        "from_country_cache": False,
        "from_tz_cache": False,
    }


@pytest.mark.parametrize(("city", "country"), [("Unrecorded City", "IT"), ("Roma", "XX")])
def test_unknown_location_requires_a_fixture(city, country):
    with pytest.raises(pytest.fail.Exception, match="add a fixture"):
        FetchGeonames(city, country).get_serialized_data()


def test_unknown_coordinates_require_a_fixture():
    fetch = FetchGeonames("Roma", "IT")
    request = Request("GET", fetch.timezone_url, params={"lat": 0, "lng": 0}).prepare()
    with pytest.raises(pytest.fail.Exception, match="add a fixture"):
        fetch.session.send(request)


def test_geonames_unit_tests_can_override_the_http_response(monkeypatch):
    fetch = FetchGeonames("Roma", "IT")
    response = Response()
    response.status_code = 200
    response._content = b'{"status": {"value": 19, "message": "hourly limit exceeded"}}'
    monkeypatch.setattr(fetch.session, "send", lambda *args, **kwargs: response)

    assert fetch.get_serialized_data() == {}


def test_unmocked_network_connections_fail_loudly():
    with socket.socket() as connection, pytest.raises(pytest.fail.Exception, match="Network access is disabled"):
        connection.connect(("127.0.0.1", 9))
