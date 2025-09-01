# backend/app/api/v1/routes/sales.py
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, conint
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ...v1.deps import get_db, get_current_user
from ....models import PromoterSale, PriceList, Store, SKU, User

router = APIRouter(prefix="/sales", tags=["sales"])


# --- Pydantic models (локально, чтобы не править schemas.py) ---

class PromoterSaleIn(BaseModel):
    store_id: int = Field(..., description="ID магазина")
    sku_id: int = Field(..., description="ID SKU")
    sold_at: date = Field(..., description="Дата продажи")
    qty: conint(gt=0) = Field(..., description="Количество")
    amount: Optional[Decimal] = Field(
        None, description="Сумма; если не передана — посчитаем по прайсу"
    )


class PromoterSaleOut(BaseModel):
    id: int
    promoter_id: int
    store_id: int
    sku_id: int
    sold_at: date
    qty: int
    amount: Decimal

    class Config:
        from_attributes = True


# --- helpers ---

def _require_promoter(user: User):
    if not user or user.role != "promoter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only promoters can use this endpoint",
        )


def _calculate_amount_if_needed(db: Session, payload: PromoterSaleIn) -> Decimal:
    """
    Если amount не передан — берём актуальную цену из прайса на дату sold_at.
    """
    if payload.amount is not None:
        # гарантируем Decimal
        return Decimal(payload.amount)

    stmt = (
        select(PriceList)
        .where(
            and_(
                PriceList.sku_id == payload.sku_id,
                PriceList.valid_from <= payload.sold_at,
                or_(PriceList.valid_to.is_(None), PriceList.valid_to >= payload.sold_at),
            )
        )
        .order_by(PriceList.valid_from.desc())
        .limit(1)
    )
    row = db.execute(stmt).scalar_one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active price for this SKU on sold_at date",
        )
    return (Decimal(row.price) * Decimal(payload.qty)).quantize(Decimal("0.01"))


def _validate_store_sku(db: Session, store_id: int, sku_id: int):
    if not db.get(Store, store_id):
        raise HTTPException(status_code=404, detail="Store not found")
    if not db.get(SKU, sku_id):
        raise HTTPException(status_code=404, detail="SKU not found")


# --- endpoints ---

@router.post("/promoter/one", response_model=PromoterSaleOut)
def add_promoter_one(
    payload: PromoterSaleIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Добавить одну продажу промоутера.
    Если amount не указан — сумма высчитывается по прайсу на дату sold_at.
    """
    _require_promoter(current_user)
    _validate_store_sku(db, payload.store_id, payload.sku_id)

    amount = _calculate_amount_if_needed(db, payload)

    sale = PromoterSale(
        promoter_id=current_user.id,
        store_id=payload.store_id,
        sku_id=payload.sku_id,
        sold_at=payload.sold_at,
        qty=int(payload.qty),
        amount=amount,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("/promoter", response_model=List[PromoterSaleOut])
def list_my_promoter_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
):
    """
    Список продаж текущего промоутера с опциональными фильтрами по датам.
    """
    _require_promoter(current_user)

    stmt = select(PromoterSale).where(PromoterSale.promoter_id == current_user.id)

    if date_from:
        stmt = stmt.where(PromoterSale.sold_at >= date_from)
    if date_to:
        stmt = stmt.where(PromoterSale.sold_at <= date_to)

    stmt = stmt.order_by(PromoterSale.sold_at.desc(), PromoterSale.id.desc())

    rows = db.execute(stmt).scalars().all()
    return rows
