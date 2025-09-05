"""Price service: overlap validation and effective price selection."""

from __future__ import annotations

from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.price import PriceList
from app.models.sku import Sku


class PriceOverlapError(Exception):
    """Raised when price periods overlap."""



def ensure_no_overlap(
    db: Session,
    sku_id: str,
    valid_from: date,
    valid_to: date | None,
    exclude_id: str | None = None,
) -> None:
    """Проверить отсутствие перекрытия цен."""
    if valid_to is not None and valid_to < valid_from:
        raise PriceOverlapError("valid_to before valid_from")
    stmt = select(PriceList).where(PriceList.sku_id == sku_id)
    if exclude_id:
        stmt = stmt.where(PriceList.id != exclude_id)
    if valid_to is not None:
        stmt = stmt.where(PriceList.valid_from <= valid_to)
    stmt = stmt.where(or_(PriceList.valid_to == None, PriceList.valid_to >= valid_from))
    exists = db.scalar(stmt.limit(1))
    if exists:
        raise PriceOverlapError("Price period overlaps")


def get_effective_price(db: Session, day: date, sku_id: str) -> PriceList | None:
    """Получить цену SKU, действующую на дату."""
    stmt = (
        select(PriceList)
        .where(
            PriceList.sku_id == sku_id,
            PriceList.valid_from <= day,
            or_(PriceList.valid_to == None, PriceList.valid_to >= day),
        )
        .order_by(PriceList.valid_from.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def get_effective_prices(db: Session, day: date) -> list[PriceList]:
    """Получить цены по всем активным SKU на дату."""
    sku_ids = db.scalars(select(Sku.id).where(Sku.active == True)).all()
    result: list[PriceList] = []
    for sku_id in sku_ids:
        price = get_effective_price(db, day, sku_id)
        if price:
            result.append(price)
    return result


__all__ = ["ensure_no_overlap", "get_effective_price", "get_effective_prices"]
