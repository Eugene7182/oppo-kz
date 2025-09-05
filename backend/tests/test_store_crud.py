"""Tests for regions, networks and stores CRUD."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.settings import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.user_service import ensure_admin
from app.core import security
from app.api.v1 import auth as auth_module


@pytest.fixture()
def client() -> TestClient:
    """Test client with in-memory DB and seeded admin."""
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    settings.admin_email = "admin@oppo.kz"
    settings.admin_password = "StrongPass123"
    object.__setattr__(settings, "SECRET_KEY", "secret")

    orig_access = auth_module.create_access_token
    orig_refresh = auth_module.create_refresh_token

    def _access(user):
        return orig_access(user.id if hasattr(user, "id") else user)

    def _refresh(user):
        return orig_refresh(user.id if hasattr(user, "id") else user)

    auth_module.create_access_token = _access
    auth_module.create_refresh_token = _refresh

    with TestingSessionLocal() as db:
        ensure_admin(db)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def auth_headers(client: TestClient) -> dict[str, str]:
    r = client.post(
        "/api/v1/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_filter_store(client: TestClient) -> None:
    headers = auth_headers(client)
    region_id = client.post(
        "/api/v1/regions", json={"name": "Almaty"}, headers=headers
    ).json()["id"]
    network_id = client.post(
        "/api/v1/networks", json={"name": "TechNet"}, headers=headers
    ).json()["id"]
    store = client.post(
        "/api/v1/stores",
        json={
            "network_id": network_id,
            "region_id": region_id,
            "code": "001",
            "name": "Main Store",
            "address": "Street 1",
        },
        headers=headers,
    ).json()
    r = client.get(
        f"/api/v1/stores?network_id={network_id}&region_id={region_id}&active=true",
        headers=headers,
    )
    data = r.json()["items"]
    assert any(row["id"] == store["id"] for row in data)


def test_store_fk_and_unique_errors(client: TestClient) -> None:
    headers = auth_headers(client)
    region_id = client.post(
        "/api/v1/regions", json={"name": "Astana"}, headers=headers
    ).json()["id"]
    network_id = client.post(
        "/api/v1/networks", json={"name": "MegaNet"}, headers=headers
    ).json()["id"]

    r = client.post(
        "/api/v1/stores",
        json={
            "network_id": "bad",
            "region_id": region_id,
            "code": "001",
            "name": "Bad",
        },
        headers=headers,
    )
    assert r.status_code == 400

    client.post(
        "/api/v1/stores",
        json={
            "network_id": network_id,
            "region_id": region_id,
            "code": "002",
            "name": "Store A",
        },
        headers=headers,
    )
    r = client.post(
        "/api/v1/stores",
        json={
            "network_id": network_id,
            "region_id": region_id,
            "code": "002",
            "name": "Store B",
        },
        headers=headers,
    )
    assert r.status_code == 400
