"""Auth flow tests."""

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

    with TestingSessionLocal() as db:
        ensure_admin(db)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_login_success(client: TestClient) -> None:
    r = client.post(
        "/api/v1/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"] and body["refresh_token"]


def test_login_wrong_password(client: TestClient) -> None:
    r = client.post(
        "/api/v1/auth/login",
        json={"email": settings.admin_email, "password": "bad"},
    )
    assert r.status_code == 401
