from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent


def test_dockerfile_does_not_use_poetry_with_pep621_pyproject():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "[project]" in pyproject
    assert "[tool.poetry]" not in pyproject
    assert "poetry install" not in dockerfile


def test_production_image_is_pinned_and_minimal():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert dockerfile.count("python:3.11.15-slim-bookworm@sha256:") == 2
    assert "pip install --no-cache-dir --require-hashes" in dockerfile
    assert "requirements.lock" in dockerfile
    assert "USER appuser" in dockerfile
    assert 'CMD ["python", "-m", "app.main"]' in dockerfile
    assert "COPY --chown=appuser:appuser . ." not in dockerfile
    assert "org.opencontainers.image.source" in dockerfile
    assert "org.opencontainers.image.licenses" in dockerfile
    assert "ENVIRONMENT=production" in dockerfile
    assert "APP_VERSION=${VERSION}" in dockerfile
    assert "GIT_REVISION=${REVISION}" in dockerfile


def test_ci_verifies_the_lock_and_runs_the_production_image():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "poetry-plugin-export==1.10.0" in workflow
    assert "diff --unified requirements.lock" in workflow
    assert "load: true" in workflow
    assert "scripts/smoke_test_container.sh" in workflow


def test_publish_is_release_tag_only_and_waits_for_verification():
    workflow = (ROOT / ".github/workflows/publish.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch" not in workflow
    assert "backend-v*" in workflow
    assert "needs: [validate-ref, verify]" in workflow
    assert "packages: write" not in workflow.split("jobs:", maxsplit=1)[0]
    assert "type=raw,value=sha-" in workflow
    assert "type=raw,value=${{ github.ref_name }}" in workflow
    assert "type=raw,value=latest" not in workflow


def test_external_github_actions_are_pinned_to_full_commit_shas():
    for workflow_path in (ROOT / ".github/workflows").glob("*.yml"):
        for line in workflow_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("uses:") or "./" in stripped:
                continue
            reference = stripped.split("@", maxsplit=1)[1].split()[0]
            assert re.fullmatch(r"[0-9a-f]{40}", reference), f"unpinned action in {workflow_path}: {line}"
            assert "# v" in line, f"missing release comment in {workflow_path}: {line}"
