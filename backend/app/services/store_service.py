"""Store service with validations."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.network import Network
from app.models.region import Region
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate


def check_fk_exist(db: Session, network_id: str, region_id: str) -> None:
    """Убедиться, что FK существуют."""
    if not db.get(Network, network_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Network not found", "code": "network_not_found"},
        )
    if not db.get(Region, region_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Region not found", "code": "region_not_found"},
        )


def ensure_unique_code_within_network(
    db: Session, network_id: str, code: str, exclude_id: str | None = None
) -> None:
    """Проверить уникальность кода внутри сети."""
    stmt = select(Store).where(Store.network_id == network_id, Store.code == code)
    if exclude_id:
        stmt = stmt.where(Store.id != exclude_id)
    exists = db.scalar(stmt)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Store code already exists", "code": "code_exists"},
        )


def create_store(db: Session, data: StoreCreate) -> Store:
    """Создать магазин с проверками."""
    check_fk_exist(db, data.network_id, data.region_id)
    ensure_unique_code_within_network(db, data.network_id, data.code)
    store = Store(
        network_id=data.network_id,
        region_id=data.region_id,
        code=data.code,
        name=data.name,
        address=data.address,
        active=True if data.active is None else data.active,
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def update_store(db: Session, store: Store, data: StoreUpdate) -> Store:
    """Обновить магазин с проверками."""
    network_id = data.network_id or store.network_id
    region_id = data.region_id or store.region_id
    check_fk_exist(db, network_id, region_id)
    code = data.code or store.code
    ensure_unique_code_within_network(db, network_id, code, exclude_id=store.id)

    if data.network_id:
        store.network_id = data.network_id
    if data.region_id:
        store.region_id = data.region_id
    if data.code:
        store.code = data.code
    if data.name is not None:
        store.name = data.name
    if data.address is not None:
        store.address = data.address
    if data.active is not None:
        store.active = data.active

    db.add(store)
    db.commit()
    db.refresh(store)
    return store


__all__ = [
    "check_fk_exist",
    "ensure_unique_code_within_network",
    "create_store",
    "update_store",
]
