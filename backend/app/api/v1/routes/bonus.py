# backend/app/api/v1/routes/bonus.py
from datetime import date
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from ....db import SessionLocal
from ....models import BonusGrid
from ....core.security import get_current_user, require_role

router = APIRouter(prefix="/bonus", tags=["bonus"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BonusOut(BaseModel):
    id: int
    sku_id: int | None = None
    network: str | None = None
    qty_from: int | None = None
    bonus_per_unit: float
    valid_from: date
    valid_to: date | None = None
    class Config:
        from_attributes = True

class BonusCreate(BaseModel):
    sku_id: int | None = None
    network: str | None = None
    qty_from: int | None = None
    bonus_per_unit: float
    valid_from: date
    valid_to: date | None = None

@router.get("", response_model=list[BonusOut])
def list_bonus(
    db: Session = Depends(get_db),
    date_on: date | None = Query(None, description="Вернуть сетки, действующие на дату"),
    sku_id: int | None = None,
    network: str | None = None,
    _: any = Depends(get_current_user),  # любой залогиненный
):
    stmt = select(BonusGrid)
    if date_on:
        stmt = stmt.where(
            and_(
                BonusGrid.valid_from <= date_on,
                (BonusGrid.valid_to == None) | (BonusGrid.valid_to >= date_on),  # noqa: E711
            )
        )
    if sku_id:
        stmt = stmt.where(BonusGrid.sku_id == sku_id)
    if network:
        stmt = stmt.where(BonusGrid.network == network)
    return db.execute(stmt).scalars().all()

@router.post("", response_model=BonusOut)
def create_bonus(body: BonusCreate, db: Session = Depends(get_db), _: any = Depends(require_role("super"))):
    b = BonusGrid(**body.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b
