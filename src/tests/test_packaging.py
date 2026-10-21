import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_pyproject_declares_fastapi_and_uvicorn():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    deps = " ".join(data["project"]["dependencies"]).lower()
    assert "fastapi" in deps
    assert "uvicorn" in deps


def test_uv_lock_present():
    assert (ROOT / "uv.lock").exists()


def test_dockerfile_is_uv_based_and_production_minded():
    text = (ROOT / "Dockerfile").read_text()
    assert "ghcr.io/astral-sh/uv" in text
    assert "uv sync" in text
    assert "--frozen" in text
    assert "USER " in text  # non-root
    assert "HEALTHCHECK" in text
    assert "uvicorn" in text
    assert "app.main:app" in text


def test_dockerignore_excludes_venv_and_git():
    text = (ROOT / ".dockerignore").read_text()
    assert ".venv" in text
    assert ".git" in text
