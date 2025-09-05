import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.settings import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.user_service import ensure_admin, create_user
from app.schemas.user import UserCreateMinimal
from app.models.user import UserRole
from app.api.v1 import auth as auth_module


@pytest.fixture()
def client() -> TestClient:
    """Test client with in-memory DB and seeded users."""

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
    settings.enable_imports = True
    object.__setattr__(settings, "secret_key", "secret")

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
        create_user(
            db,
            UserCreateMinimal(
                email="promo@oppo.kz", password="StrongPass123", role=UserRole.promoter
            ),
        )

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    auth_module.create_access_token = orig_access
    auth_module.create_refresh_token = orig_refresh


def auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_promoter_sale_approve_and_filter(client: TestClient) -> None:
    admin_h = auth_headers(client, settings.admin_email, settings.admin_password)
    region_id = client.post("/api/v1/regions", json={"name": "R"}, headers=admin_h).json()["id"]
    network_id = client.post("/api/v1/networks", json={"name": "N"}, headers=admin_h).json()["id"]
    store_id = client.post(
        "/api/v1/stores",
        json={"network_id": network_id, "region_id": region_id, "code": "S1", "name": "Store"},
        headers=admin_h,
    ).json()["id"]
    sku_id = client.post(
        "/api/v1/sku",
        json={"brand": "B", "model": "M"},
        headers=admin_h,
    ).json()["id"]
    promo_h = auth_headers(client, "promo@oppo.kz", "StrongPass123")
    sale = client.post(
        "/api/v1/sales/promoters",
        json={
            "store_id": store_id,
            "sku_id": sku_id,
            "qty": 1,
            "amount": 100,
            "sold_at": "2024-01-01",
        },
        headers=promo_h,
    ).json()
    sale_id = sale["id"]
    client.post(f"/api/v1/sales/promoters/{sale_id}/approve", headers=admin_h)
    r = client.put(
        f"/api/v1/sales/promoters/{sale_id}",
        json={"qty": 2},
        headers=promo_h,
    )
    assert r.status_code == 409
    r = client.get("/api/v1/sales/promoters?approved=true", headers=admin_h)
    assert any(item["id"] == sale_id for item in r.json()["items"])


def test_retail_import(client: TestClient) -> None:
    admin_h = auth_headers(client, settings.admin_email, settings.admin_password)
    region_id = client.post("/api/v1/regions", json={"name": "R"}, headers=admin_h).json()["id"]
    network_id = client.post("/api/v1/networks", json={"name": "N"}, headers=admin_h).json()["id"]
    store_id = client.post(
        "/api/v1/stores",
        json={"network_id": network_id, "region_id": region_id, "code": "S1", "name": "Store"},
        headers=admin_h,
    ).json()["id"]
    sku_id = client.post(
        "/api/v1/sku",
        json={"brand": "B", "model": "M"},
        headers=admin_h,
    ).json()["id"]
    payload = {
        "items": [
            {
                "store_id": store_id,
                "sku_id": sku_id,
                "qty": 2,
                "amount": 200,
                "sold_at": "2024-01-01",
                "external_id": "X1",
                "feed_batch_id": "B1",
            },
            {
                "store_id": store_id,
                "sku_id": sku_id,
                "qty": 2,
                "amount": 210,
                "sold_at": "2024-01-01",
                "external_id": "X1",
                "feed_batch_id": "B1",
            },
        ]
    }
    r = client.post("/api/v1/sales/retail/import", json=payload, headers=admin_h)
    data = r.json()
    assert data["created"] == 1
    assert data["skipped"] == ["X1"]
    r = client.get("/api/v1/sales/retail?feed_batch_id=B1", headers=admin_h)
    assert len(r.json()["items"]) == 1
