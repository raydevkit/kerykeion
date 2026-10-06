"""Replay recorded GeoNames HTTP responses; tests never need external connections.

The regression gate also loads this file as a plugin for the base's own tests.
"""

import json
from pathlib import Path
import socket
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlsplit

import pytest
from requests import Response
from requests_cache import CachedSession


def pytest_configure(config):
    # Install before collection: module-level subjects must also stay offline.
    searches = {}
    timezones = {}
    for path in sorted((Path(__file__).parent / "fixtures" / "geonames").glob("*.json")):
        recording = json.loads(path.read_text(encoding="utf-8"))
        query = recording["query"]
        searches[(query["q"], query["country"])] = recording["search"]
        location = recording["search"]["geonames"][0]
        timezones[(location["lat"], location["lng"])] = recording["timezone"]

    def send(session, request, **kwargs):
        url = urlsplit(request.url)
        query = dict(parse_qs(url.query, keep_blank_values=True))
        if request.method != "GET" or url.hostname != "api.geonames.org":
            pytest.fail(f"Unexpected HTTP request in offline tests: {request.method} {url.hostname}{url.path}")
        if url.path == "/searchJSON":
            key = (query.get("q", [""])[0], query.get("country", [""])[0])
            payload = searches.get(key)
        elif url.path == "/timezoneJSON":
            key = (query.get("lat", [""])[0], query.get("lng", [""])[0])
            payload = timezones.get(key)
        else:
            pytest.fail(f"Unexpected GeoNames endpoint: {url.path}; add a fixture in tests/fixtures/geonames/")
        if payload is None:
            pytest.fail(f"Unrecorded GeoNames {url.path} lookup {key!r}; add a fixture in tests/fixtures/geonames/")
        response = Response()
        response.status_code = 200
        response.url = request.url
        response.request = request
        response.encoding = "utf-8"
        response._content = json.dumps(payload).encode("utf-8")
        response.from_cache = False
        return response

    def deny_network(*args, **kwargs):
        pytest.fail("Network access is disabled in tests; add a fixture or mock the HTTP transport")

    # Keep even the unused SQLite cache out of the checkout/user cache.
    cache = TemporaryDirectory(prefix="kerykeion-test-geonames-")
    config.add_cleanup(cache.cleanup)
    patch = pytest.MonkeyPatch()
    config.add_cleanup(patch.undo)
    patch.setenv("KERYKEION_GEONAMES_CACHE_NAME", str(Path(cache.name) / "cache"))
    patch.setattr(CachedSession, "send", send)
    patch.setattr(socket.socket, "connect", deny_network)
    patch.setattr(socket.socket, "connect_ex", deny_network)
    patch.setattr(socket, "getaddrinfo", deny_network)
