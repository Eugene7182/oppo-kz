"""Region endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, rbac_required
from app.db.session import get_db
from app.models.region import Region
from app.models.user import UserRole
from app.schemas.region import RegionCreate, RegionRead, RegionUpdate

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("", dependencies=[Depends(get_current_user)], response_model=dict)
def list_regions(
    limit: int = 100,
    offset: int = 0,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Список регионов с фильтром по имени."""
    stmt = select(Region)
    if q:
        stmt = stmt.where(Region.name.ilike(f"%{q}%"))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Region.name).offset(offset).limit(limit)).all()
    items = [RegionRead.model_validate(r) for r in rows]
    return {"items": items, "total": total}


_admin_office = rbac_required([UserRole.admin, UserRole.office])


@router.post("", dependencies=[Depends(_admin_office)], response_model=RegionRead, status_code=status.HTTP_201_CREATED)
def create_region(data: RegionCreate, db: Session = Depends(get_db)) -> Region:
    """Создать регион."""
    exists = db.scalar(select(Region).where(Region.name == data.name))
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Region already exists", "code": "region_exists"},
        )
    region = Region(name=data.name)
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


@router.put("/{region_id}", dependencies=[Depends(_admin_office)], response_model=RegionRead)
def update_region(region_id: str, data: RegionUpdate, db: Session = Depends(get_db)) -> Region:
    """Обновить регион."""
    region = db.get(Region, region_id)
    if not region:
        raise HTTPException(status_code=404, detail={"detail": "Region not found", "code": "region_not_found"})
    if data.name != region.name:
        exists = db.scalar(select(Region).where(Region.name == data.name, Region.id != region_id))
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": "Region already exists", "code": "region_exists"},
            )
        region.name = data.name
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


@router.delete("/{region_id}", dependencies=[Depends(_admin_office)], response_model=RegionRead)
def delete_region(region_id: str, db: Session = Depends(get_db)) -> Region:
    """Удалить регион."""
    region = db.get(Region, region_id)
    if not region:
        raise HTTPException(status_code=404, detail={"detail": "Region not found", "code": "region_not_found"})
    db.delete(region)
    db.commit()
    return region


__all__ = ["router"]
