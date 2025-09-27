# backend/app/api/v1/routes/price_list.py
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

# Мы в app/api/v1/routes → к core/models/schemas выходим ЧЕТЫРЬМЯ точками
from ....models import PriceList, SKU
from ....schemas import PriceListIn, PriceListOut
from ..deps import get_db, require_super

router = APIRouter()

def to_out(row: PriceList) -> PriceListOut:
    return PriceListOut(
        id=row.id,
        sku_id=row.sku_id,
        price=float(row.price),
        valid_from=row.valid_from,
        valid_to=row.valid_to,
    )

@router.get("/", response_model=list[PriceListOut])
def list_prices(
    db: Session = Depends(get_db),
    sku_id: int | None = None,
    on: date | None = None,
):
    # если on не передали — берём сегодняшнюю дату
    if on is None:
        on = date.today()

    stmt = select(PriceList).order_by(PriceList.sku_id, PriceList.valid_from.desc())

    if sku_id is not None:
        stmt = stmt.where(PriceList.sku_id == sku_id)

    # активные на дату on
    stmt = stmt.where(
        and_(
            PriceList.valid_from <= on,
            (PriceList.valid_to.is_(None)) | (PriceList.valid_to >= on),
        )
    )

    rows = db.scalars(stmt).all()
    return [to_out(r) for r in rows]

@router.post("/", response_model=PriceListOut, dependencies=[Depends(require_super())])
def create_price(item: PriceListIn, db: Session = Depends(get_db)):
    # проверим, что SKU существует
    sku = db.get(SKU, item.sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    # закрываем предыдущую «бесконечную» цену, чтобы не было перекрытия
    prev_stmt = (
        select(PriceList)
        .where(
            and_(
                PriceList.sku_id == item.sku_id,
                PriceList.valid_to.is_(None),
                PriceList.valid_from <= item.valid_from,
            )
        )
        .order_by(PriceList.valid_from.desc())
    )
    prev = db.scalars(prev_stmt).first()
    if prev:
        prev.valid_to = item.valid_from - timedelta(days=1)

    row = PriceList(
        sku_id=item.sku_id,
        price=item.price,
        valid_from=item.valid_from,
        valid_to=item.valid_to,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return to_out(row)
