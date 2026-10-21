import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def client():
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def test_app_factory_returns_fastapi_instance():
    from fastapi import FastAPI

    from app.main import create_app

    assert isinstance(create_app(), FastAPI)


def test_module_level_app_exposed_for_uvicorn():
    from app.main import app

    assert app is not None


def test_liveness_endpoint(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readiness_endpoint(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_settings_loaded_from_env(monkeypatch):
    from app.core.config import Settings

    monkeypatch.setenv("APP_NAME", "my-service")
    assert Settings().app_name == "my-service"


def test_openapi_title_uses_settings(client):
    assert client.get("/openapi.json").json()["info"]["title"]


def test_request_id_header_generated(client):
    r = client.get("/health/live")
    assert r.headers.get("x-request-id")


def test_request_id_header_propagated(client):
    r = client.get("/health/live", headers={"X-Request-ID": "abc-123"})
    assert r.headers["x-request-id"] == "abc-123"


def test_unknown_route_returns_json_404(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert "detail" in r.json()


def test_versioned_api_router_mounted(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert any(p.startswith("/api/v1") for p in paths)
