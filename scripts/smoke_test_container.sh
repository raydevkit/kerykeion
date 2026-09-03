#!/usr/bin/env bash
set -euo pipefail

image=${1:?usage: smoke_test_container.sh IMAGE VERSION REVISION}
version=${2:?usage: smoke_test_container.sh IMAGE VERSION REVISION}
revision=${3:?usage: smoke_test_container.sh IMAGE VERSION REVISION}
prefix="kerykeion-smoke-$$"
missing_key_container="${prefix}-missing-key"
default_key_container="${prefix}-default-key"
running_container="${prefix}-running"
api_key="ci-production-api-key-0123456789abcdef"

cleanup() {
    docker rm --force "$missing_key_container" "$default_key_container" "$running_container" >/dev/null 2>&1 || true
}
trap cleanup EXIT

assert_startup_fails() {
    local container=$1
    shift
    docker run --detach --name "$container" "$@" "$image" >/dev/null
    for _ in {1..20}; do
        if [[ $(docker inspect --format '{{.State.Running}}' "$container") == "false" ]]; then
            [[ $(docker inspect --format '{{.State.ExitCode}}' "$container") != "0" ]]
            return
        fi
        sleep 0.25
    done
    echo "container unexpectedly remained running: $container" >&2
    return 1
}

assert_startup_fails "$missing_key_container"
assert_startup_fails "$default_key_container" --env API_KEY=your-secret-api-key-change-this-in-production

[[ $(docker image inspect --format '{{.Config.User}}' "$image") == "appuser" ]]
[[ $(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' "$image") == "$version" ]]
[[ $(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' "$image") == "$revision" ]]
[[ $(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.source"}}' "$image") == "https://github.com/raydevkit/kerykeion" ]]
[[ $(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.licenses"}}' "$image") == "AGPL-3.0" ]]

docker run --detach --name "$running_container" --env API_KEY="$api_key" "$image" >/dev/null
for _ in {1..30}; do
    if docker exec "$running_container" python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

[[ $(docker inspect --format '{{.State.Running}}' "$running_container") == "true" ]]
[[ $(docker exec "$running_container" id -u) == "10001" ]]

docker exec --interactive "$running_container" python - "$api_key" "$version" "$revision" <<'PY'
import json
import sys
import urllib.error
import urllib.request


base_url = "http://127.0.0.1:8000"
api_key, version, revision = sys.argv[1:]


def request(path, key=None):
    headers = {"X-API-Key": key} if key is not None else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(base_url + path, headers=headers), timeout=10) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


assert request("/health")[0] == 200
assert request("/api/v1/sky/now")[0] == 401
assert request("/api/v1/sky/now", "wrong")[0] == 403
assert request("/api/v1/sky/now", api_key)[0] == 200
for path in ("/docs", "/redoc", "/openapi.json"):
    assert request(path)[0] == 404

status, body = request("/")
root = json.loads(body)
assert status == 200
assert root["version"] == version
assert root["revision"] == revision
assert root["source"] == f"https://github.com/raydevkit/kerykeion/tree/{revision}"
assert "docs" not in root
PY

for path in /app/.env /app/.git /app/tests /app/docs /app/pyproject.toml /app/requirements.lock; do
    ! docker exec "$running_container" test -e "$path"
done
