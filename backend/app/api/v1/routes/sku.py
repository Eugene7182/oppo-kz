# backend/app/api/v1/routes/sku.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from app.security_rbac import require_roles
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db
from ....models import SKU  # у тебя модели импортируются из монолитного app.models
from app.schemas.sku import SKUOut  # абсолютный импорт, чтобы не зависеть от __init__.py

router = APIRouter(prefix="/sku", tags=["sku"])

@router.get("", response_model=list[SKUOut], dependencies=[Depends(require_roles("admin", "office", "supervisor"))])
def list_sku(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Отдаём список SKU (пагинация через limit/offset).
    """
    stmt = select(SKU).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    return rows

@router.get("/{sku_id}", response_model=SKUOut, dependencies=[Depends(require_roles("admin", "office", "supervisor"))])
def get_sku(sku_id: str, db: Session = Depends(get_db)):
    """
    Получить одну SKU по id.
    """
    obj = db.get(SKU, sku_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SKU not found")
    return obj
