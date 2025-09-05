from decimal import Decimal
from datetime import date

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


def test_effective_price(client: TestClient) -> None:
    headers = auth_headers(client)
    sku_id = client.post(
        "/api/v1/sku",
        json={"brand": "OPPO", "model": "A1"},
        headers=headers,
    ).json()["id"]
    client.post(
        "/api/v1/prices",
        json={
            "sku_id": sku_id,
            "price": "100.00",
            "valid_from": "2024-01-01",
            "valid_to": "2024-03-31",
        },
        headers=headers,
    )
    client.post(
        "/api/v1/prices",
        json={
            "sku_id": sku_id,
            "price": "200.00",
            "valid_from": "2024-04-01",
        },
        headers=headers,
    )
    r1 = client.get(
        f"/api/v1/prices/effective?date=2024-02-01&sku_id={sku_id}", headers=headers
    )
    r2 = client.get(
        f"/api/v1/prices/effective?date=2024-05-01&sku_id={sku_id}", headers=headers
    )
    assert Decimal(r1.json()["price"]) == Decimal("100.00")
    assert Decimal(r2.json()["price"]) == Decimal("200.00")


def test_price_overlap(client: TestClient) -> None:
    headers = auth_headers(client)
    sku_id = client.post(
        "/api/v1/sku",
        json={"brand": "OPPO", "model": "B1"},
        headers=headers,
    ).json()["id"]
    client.post(
        "/api/v1/prices",
        json={
            "sku_id": sku_id,
            "price": "150.00",
            "valid_from": "2024-01-01",
            "valid_to": "2024-01-31",
        },
        headers=headers,
    )
    r = client.post(
        "/api/v1/prices",
        json={
            "sku_id": sku_id,
            "price": "160.00",
            "valid_from": "2024-01-15",
            "valid_to": "2024-02-15",
        },
        headers=headers,
    )
    assert r.status_code == 400
    assert r.json()["code"] == "price_overlap"


def test_effective_all_sku(client: TestClient) -> None:
    headers = auth_headers(client)
    sku1 = client.post(
        "/api/v1/sku",
        json={"brand": "OPPO", "model": "C1"},
        headers=headers,
    ).json()["id"]
    sku2 = client.post(
        "/api/v1/sku",
        json={"brand": "OPPO", "model": "C2"},
        headers=headers,
    ).json()["id"]
    client.post(
        "/api/v1/prices",
        json={"sku_id": sku1, "price": "100.00", "valid_from": "2024-01-01"},
        headers=headers,
    )
    client.post(
        "/api/v1/prices",
        json={"sku_id": sku2, "price": "200.00", "valid_from": "2024-01-01"},
        headers=headers,
    )
    r = client.get("/api/v1/prices/effective?date=2024-01-10", headers=headers)
    data = r.json()
    assert isinstance(data, list)
    assert {row["sku_id"] for row in data} == {sku1, sku2}
