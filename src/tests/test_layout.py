"""Project layout: modern `src/` layout with an installable package."""
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "app"


def test_package_lives_under_src():
    for rel in ("__init__.py", "main.py", "api/health.py", "api/v1/router.py",
                "core/config.py", "agents/content_writer.py"):
        assert (SRC / rel).is_file(), f"missing src/app/{rel}"


def test_no_top_level_app_package_left():
    assert not (ROOT / "app").exists()


def test_pyproject_defines_build_system_and_packages_src():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert "build-system" in data
    assert data["tool"]["uv"].get("package") is not False


def test_pytest_uses_src_on_path():
    text = (ROOT / "pytest.ini").read_text()
    assert "src" in text


def test_dockerfile_copies_src():
    text = (ROOT / "Dockerfile").read_text()
    assert "src" in text
    assert "app.main:app" in text


def test_tests_live_under_src():
    assert (ROOT / "src" / "tests" / "test_layout.py").is_file()
    assert not (ROOT / "tests").exists()
