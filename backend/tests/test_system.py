# backend/tests/test_system.py
from fastapi.testclient import TestClient

from app.main import app
from app.core.settings import settings

client = TestClient(app)


def test_health() -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert isinstance(body.get("db"), bool)


def test_version() -> None:
    r = client.get("/api/v1/version")
    assert r.status_code == 200
    body = r.json()
    assert body.get("version") == settings.version
    assert body.get("commit") == settings.git_commit
