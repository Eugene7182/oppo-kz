"""Integration tests for invites, sales, periods, and plans."""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.main import app
import app.main as main_module
from app.core.security import get_db, get_password_hash
from app.models.region import Region
from app.models.network import Network
from app.models.store import Store
from app.models.product import Product
from app.models.user import User, UserRole, UserStatus


@pytest.fixture()
def client() -> TestClient:
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    test_data: dict[str, str] = {}

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    main_module.seed_admin = lambda db: None  # type: ignore[assignment]

    with TestingSessionLocal() as db:
        region = Region(name="Almaty")
        other_region = Region(name="Astana")
        network = Network(name="Sulpak")
        db.add_all([region, other_region, network])
        db.flush()
        store = Store(network_id=network.id, region_id=region.id, code="S1", name="Mega")
        product = Product(sku="SKU-1", name="Find X")
        db.add_all([store, product])
        db.flush()
        test_data.update(
            {
                "region_id": region.id,
                "other_region_id": other_region.id,
                "store_id": store.id,
                "product_id": product.id,
            }
        )

        users = [
            User(
                email="admin@oppo.kz",
                full_name="Admin",
                role=UserRole.admin,
                hashed_password=get_password_hash("adminpass"),
                status=UserStatus.active,
            ),
            User(
                email="office@oppo.kz",
                full_name="Office",
                role=UserRole.office,
                hashed_password=get_password_hash("officepass"),
                status=UserStatus.active,
            ),
            User(
                email="super@oppo.kz",
                full_name="Supervisor",
                role=UserRole.supervisor,
                hashed_password=get_password_hash("superpass"),
                status=UserStatus.active,
                region_id=region.id,
            ),
            User(
                email="promo@oppo.kz",
                full_name="Promoter",
                role=UserRole.promoter,
                hashed_password=get_password_hash("promopass"),
                status=UserStatus.active,
                region_id=region.id,
            ),
        ]
        db.add_all(users)
        db.commit()

    with TestClient(app) as c:
        c.region_id = test_data["region_id"]  # type: ignore[attr-defined]
        c.other_region_id = test_data["other_region_id"]  # type: ignore[attr-defined]
        c.store_id = test_data["store_id"]  # type: ignore[attr-defined]
        c.product_id = test_data["product_id"]  # type: ignore[attr-defined]
        yield c

    app.dependency_overrides.clear()


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token_resp = client.post(
        "/api/v1/auth/login",
        json={"username": email, "password": password},
    )
    assert token_resp.status_code == 200, token_resp.text
    token = token_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_supervisor_invite_scope(client: TestClient) -> None:
    supervisor_h = _auth_headers(client, "super@oppo.kz", "superpass")

    payload = {
        "email": "newpromo@oppo.kz",
        "role_requested": "promoter",
    }
    resp = client.post("/api/v1/invites", json=payload, headers=supervisor_h)
    assert resp.status_code == 201, resp.text
    invite = resp.json()
    assert invite["scope_type"] == "region"
    assert invite["scope_id"] == client.region_id

    forbidden = client.post(
        "/api/v1/invites",
        json={
            "email": "fail@oppo.kz",
            "role_requested": "promoter",
            "scope_type": "region",
            "scope_id": client.other_region_id,
        },
        headers=supervisor_h,
    )
    assert forbidden.status_code == 403


def test_sale_idempotency_and_versioning(client: TestClient) -> None:
    promoter_h = _auth_headers(client, "promo@oppo.kz", "promopass")

    sale_id = str(uuid.uuid4())
    payload = {
        "sale_id": sale_id,
        "date": date.today().isoformat(),
        "store_id": client.store_id,
        "sku_id": client.product_id,
        "qty": 2,
        "price": 1000,
    }
    resp = client.post("/api/v1/sales", json=payload, headers=promoter_h)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["version"] == 1

    # Idempotent by sale_id
    second = client.post("/api/v1/sales", json=payload, headers=promoter_h)
    assert second.status_code == 201
    assert second.json()["version"] == 1

    # Version conflict
    mismatch = client.patch(
        f"/api/v1/sales/{sale_id}",
        json={"qty": 3},
        headers={**promoter_h, "If-Match": "999"},
    )
    assert mismatch.status_code == 409
    assert mismatch.json()["detail"]["code"] == "version_conflict"

    update = client.patch(
        f"/api/v1/sales/{sale_id}",
        json={"qty": 5},
        headers={**promoter_h, "If-Match": "1"},
    )
    assert update.status_code == 200
    assert update.json()["version"] == 2


def test_period_lock_and_correction(client: TestClient) -> None:
    promoter_h = _auth_headers(client, "promo@oppo.kz", "promopass")
    admin_h = _auth_headers(client, "admin@oppo.kz", "adminpass")

    sale_id = str(uuid.uuid4())
    payload = {
        "sale_id": sale_id,
        "date": date.today().isoformat(),
        "store_id": client.store_id,
        "sku_id": client.product_id,
        "qty": 1,
        "price": 500,
    }
    assert client.post("/api/v1/sales", json=payload, headers=promoter_h).status_code == 201

    close = client.post(
        "/api/v1/periods/close",
        json={
            "from_date": date.today().isoformat(),
            "to_date": date.today().isoformat(),
            "scope": "store",
            "scope_id": client.store_id,
        },
        headers=admin_h,
    )
    assert close.status_code == 201, close.text

    locked = client.patch(
        f"/api/v1/sales/{sale_id}",
        json={"qty": 2},
        headers={**promoter_h, "If-Match": "1"},
    )
    assert locked.status_code == 409
    assert locked.json()["detail"]["code"] == "locked_period"

    correction = client.post(
        f"/api/v1/sales/{sale_id}/corrections",
        json={"delta_qty": 1, "delta_price": 100, "reason": "Late report"},
        headers=admin_h,
    )
    assert correction.status_code == 201

    listing = client.get("/api/v1/sales", headers=admin_h)
    assert listing.status_code == 200
    items = listing.json()["items"]
    target = next(item for item in items if item["id"] == sale_id)
    assert target["corrected"] is True
    assert target["fact_qty"] == 2


def test_plan_bulk_and_patch(client: TestClient) -> None:
    office_h = _auth_headers(client, "office@oppo.kz", "officepass")
    promoter_h = _auth_headers(client, "promo@oppo.kz", "promopass")
    promoter_info = client.get("/api/v1/auth/me", headers=promoter_h)
    assert promoter_info.status_code == 200
    promoter_id = promoter_info.json()["id"]

    bulk_payload = [
        {
            "period_ym": "2024-09",
            "promoter_id": promoter_id,
            "store_id": client.store_id,
            "target_units": 10,
            "target_revenue": 10000,
            "reason": "Initial plan",
        }
    ]

    created = client.post("/api/v1/plans/promoter-month/bulk", json=bulk_payload, headers=office_h)
    assert created.status_code == 201, created.text
    plan = created.json()["items"][0]

    conflict = client.patch(
        f"/api/v1/plans/promoter-month/{plan['id']}",
        json={"target_units": 12},
        headers={**office_h, "If-Match": "99"},
    )
    assert conflict.status_code == 409

    patched = client.patch(
        f"/api/v1/plans/promoter-month/{plan['id']}",
        json={"target_units": 12, "reason": "Adjust"},
        headers={**office_h, "If-Match": str(plan["version"])}
    )
    assert patched.status_code == 200
    assert patched.json()["version"] == plan["version"] + 1
