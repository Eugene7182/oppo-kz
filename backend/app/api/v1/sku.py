from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, rbac_required
from app.db.session import get_db
from app.models.sku import Sku
from app.models.user import UserRole
from app.schemas.sku import SkuCreate, SkuRead, SkuUpdate

router = APIRouter(prefix="/sku", tags=["sku"])


@router.get("", dependencies=[Depends(get_current_user)], response_model=dict)
def list_sku(
    limit: int = 100,
    offset: int = 0,
    q: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Список SKU с фильтрами."""
    stmt = select(Sku)
    if q:
        stmt = stmt.where(or_(Sku.brand.ilike(f"%{q}%"), Sku.model.ilike(f"%{q}%")))
    if active is not None:
        stmt = stmt.where(Sku.active == active)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Sku.brand, Sku.model).offset(offset).limit(limit)).all()
    items = [SkuRead.model_validate(r) for r in rows]
    return {"items": items, "total": total}


_admin_office = rbac_required([UserRole.admin, UserRole.office])


@router.post("", dependencies=[Depends(_admin_office)], response_model=SkuRead, status_code=status.HTTP_201_CREATED)
def create_sku_endpoint(data: SkuCreate, db: Session = Depends(get_db)) -> Sku:
    """Создать SKU."""
    sku = Sku(
        brand=data.brand,
        model=data.model,
        attrs=data.attrs,
        active=True if data.active is None else data.active,
    )
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku


@router.put("/{sku_id}", dependencies=[Depends(_admin_office)], response_model=SkuRead)
def update_sku_endpoint(sku_id: str, data: SkuUpdate, db: Session = Depends(get_db)) -> Sku:
    """Обновить SKU."""
    sku = db.get(Sku, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail={"detail": "Sku not found", "code": "sku_not_found"})
    if data.brand is not None:
        sku.brand = data.brand
    if data.model is not None:
        sku.model = data.model
    if data.attrs is not None:
        sku.attrs = data.attrs
    if data.active is not None:
        sku.active = data.active
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku


@router.delete("/{sku_id}", dependencies=[Depends(_admin_office)], response_model=SkuRead)
def delete_sku_endpoint(sku_id: str, db: Session = Depends(get_db)) -> Sku:
    """Мягкое удаление SKU: active=false."""
    sku = db.get(Sku, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail={"detail": "Sku not found", "code": "sku_not_found"})
    sku.active = False
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku


__all__ = ["router"]
