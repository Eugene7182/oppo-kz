"""Store endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, func, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, rbac_required
from app.db.session import get_db
from app.models.store import Store
from app.models.user import UserRole
from app.schemas.store import StoreCreate, StoreRead, StoreUpdate
from app.services.store_service import create_store, update_store

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", dependencies=[Depends(get_current_user)], response_model=dict)
def list_stores(
    limit: int = 100,
    offset: int = 0,
    network_id: str | None = None,
    region_id: str | None = None,
    active: bool | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Список магазинов с фильтрами."""
    stmt = select(Store)
    if network_id:
        stmt = stmt.where(Store.network_id == network_id)
    if region_id:
        stmt = stmt.where(Store.region_id == region_id)
    if active is not None:
        stmt = stmt.where(Store.active == active)
    if q:
        stmt = stmt.where(or_(Store.name.ilike(f"%{q}%"), Store.code.ilike(f"%{q}%")))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Store.name).offset(offset).limit(limit)).all()
    items = [StoreRead.model_validate(r) for r in rows]
    return {"items": items, "total": total}


_admin_office = rbac_required([UserRole.admin, UserRole.office])


@router.post("", dependencies=[Depends(_admin_office)], response_model=StoreRead, status_code=status.HTTP_201_CREATED)
def create_store_endpoint(data: StoreCreate, db: Session = Depends(get_db)) -> Store:
    """Создать магазин."""
    return create_store(db, data)


@router.put("/{store_id}", dependencies=[Depends(_admin_office)], response_model=StoreRead)
def update_store_endpoint(store_id: str, data: StoreUpdate, db: Session = Depends(get_db)) -> Store:
    """Обновить магазин."""
    store = db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail={"detail": "Store not found", "code": "store_not_found"})
    return update_store(db, store, data)


@router.delete("/{store_id}", dependencies=[Depends(_admin_office)], response_model=StoreRead)
def delete_store_endpoint(store_id: str, db: Session = Depends(get_db)) -> Store:
    """Мягкое удаление магазина: active=false."""
    store = db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail={"detail": "Store not found", "code": "store_not_found"})
    store.active = False
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


__all__ = ["router"]
