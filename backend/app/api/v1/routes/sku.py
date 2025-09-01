# backend/app/api/v1/routes/sku.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ....models import SKU
from ....schemas import SKUOut
from ..deps import get_db, require_super

router = APIRouter(prefix="/sku", tags=["sku"])


@router.get("", response_model=list[SKUOut])
def list_sku(db: Session = Depends(get_db)):
    rows = db.scalars(select(SKU).order_by(SKU.brand, SKU.model, SKU.code)).all()
    return rows


class SKUIn(BaseModel):
    brand: str
    model: str
    code: str


@router.post("", response_model=SKUOut, dependencies=[Depends(require_super())])
def create_sku(body: SKUIn, db: Session = Depends(get_db)):
    exists = db.scalar(select(SKU).where(SKU.code == body.code.strip()))
    if exists:
        raise HTTPException(status_code=409, detail="SKU code already exists")

    row = SKU(brand=body.brand.strip(), model=body.model.strip(), code=body.code.strip())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
