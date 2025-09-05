"""Feature flag tests."""

from fastapi.testclient import TestClient

from app.core.settings import settings
from app.main import app


def test_bonuses_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "enable_bonuses", False)
    client = TestClient(app)
    r = client.get("/api/v1/bonuses/ping")
    assert r.status_code == 404
    assert r.json() == {"detail": "Feature disabled", "code": "feature_disabled"}


def test_bonuses_enabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "enable_bonuses", True)
    client = TestClient(app)
    r = client.get("/api/v1/bonuses/ping")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "feature": "bonuses"}

