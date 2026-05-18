from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_dockerfile_does_not_use_poetry_with_pep621_pyproject():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "[project]" in pyproject
    assert "[tool.poetry]" not in pyproject
    assert "poetry install" not in dockerfile
