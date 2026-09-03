from pathlib import Path


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
    assert '"--workers", "2"' in dockerfile
    assert "COPY --chown=appuser:appuser . ." not in dockerfile
    assert "org.opencontainers.image.source" in dockerfile
    assert "org.opencontainers.image.licenses" in dockerfile
