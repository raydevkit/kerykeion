#!/usr/bin/env bash
set -euo pipefail

mode=${1:?usage: run_regression_gate.sh pr|ancestor TESTED_SHA [EXPECTED_BASE_SHA]}
tested_sha=${2:?usage: run_regression_gate.sh pr|ancestor TESTED_SHA [EXPECTED_BASE_SHA]}
expected_base_sha=${3:-}
python_bin=${PYTHON_BIN:-python}
repository=$(git rev-parse --show-toplevel)
checker="$repository/scripts/check_regression_baseline.py"
baseline="$repository/.github/pytest-regression-baseline.json"
gate_dir=$(mktemp -d /tmp/kerykeion-regression.XXXXXX)
base_worktree="$gate_dir/base"
base_venv="$gate_dir/base-venv"
head_results="$gate_dir/head.json"
base_results="$gate_dir/base.json"
poetry_python=$(head -n 1 "$(command -v poetry)" | sed -E 's/^#![[:space:]]*([^[:space:]]+).*/\1/')

[[ "$tested_sha" =~ ^[0-9a-fA-F]{40}$ ]]
[[ "$(git -C "$repository" rev-parse HEAD)" == "${tested_sha,,}" ]]

cleanup() {
    git -C "$repository" worktree remove --force "$base_worktree" >/dev/null 2>&1 || true
    rm -r "$gate_dir"
}
trap cleanup EXIT

case "$mode" in
    pr)
        [[ -n "$expected_base_sha" ]]
        baseline_sha=$(poetry -C "$repository" run python "$checker" base-sha --baseline "$baseline" --expected-base-sha "$expected_base_sha")
        ;;
    ancestor)
        baseline_sha=$(poetry -C "$repository" run python "$checker" base-sha --baseline "$baseline")
        ;;
    *)
        echo "mode must be pr or ancestor" >&2
        exit 2
        ;;
esac

git -C "$repository" fetch --no-tags origin "$baseline_sha"
poetry -C "$repository" run python "$checker" collect --tests-root "$repository/tests" --output "$head_results"

if [[ "$mode" == "ancestor" ]]; then
    poetry -C "$repository" run python "$checker" verify-ancestor \
        --baseline "$baseline" \
        --head-results "$head_results" \
        --repository "$repository" \
        --tested-sha "$tested_sha"
    exit
fi

git -C "$repository" worktree add --detach "$base_worktree" "$baseline_sha"

# The reviewed base lock has a stale Poetry content hash. Refresh only that
# metadata in the isolated copy so Poetry installs its original locked packages.
content_hash=$("$poetry_python" - "$base_worktree" <<'PY'
import sys
from pathlib import Path

from poetry.factory import Factory


project = Factory().create_poetry(Path(sys.argv[1]))
print(project.locker._get_content_hash())
PY
)
"$python_bin" - "$base_worktree/poetry.lock" "$content_hash" <<'PY'
import re
import sys
from pathlib import Path


path = Path(sys.argv[1])
updated, count = re.subn(
    r'(?m)^content-hash = "[0-9a-f]{64}"$',
    f'content-hash = "{sys.argv[2]}"',
    path.read_text(encoding="utf-8"),
)
if count != 1:
    raise SystemExit("expected exactly one Poetry content hash")
path.write_text(updated, encoding="utf-8")
PY

"$python_bin" -m venv "$base_venv"
VIRTUAL_ENV="$base_venv" PATH="$base_venv/bin:$PATH" POETRY_VIRTUALENVS_CREATE=false \
    poetry -C "$base_worktree" install --only main --no-root --no-interaction

mapfile -t locked_test_tools < <("$python_bin" - "$base_worktree/poetry.lock" <<'PY'
import sys
import tomllib


with open(sys.argv[1], "rb") as lock_file:
    packages = tomllib.load(lock_file)["package"]
versions = {package["name"]: package["version"] for package in packages}
for name in ("pytest", "pytest-asyncio", "httpx"):
    if name not in versions:
        raise SystemExit(f"{name} is missing from the base lock")
    print(f"{name}=={versions[name]}")
PY
)
"$base_venv/bin/pip" install --disable-pip-version-check "${locked_test_tools[@]}"
"$base_venv/bin/python" "$checker" collect --tests-root "$base_worktree/tests" --offline-geonames --output "$base_results"
poetry -C "$repository" run python "$checker" verify-pr \
    --baseline "$baseline" \
    --expected-base-sha "$expected_base_sha" \
    --base-results "$base_results" \
    --head-results "$head_results"
