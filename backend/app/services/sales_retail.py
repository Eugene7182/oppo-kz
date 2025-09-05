from __future__ import annotations

"""Business logic for retail sales and batch import."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sales_retail import SalesRetail
from app.schemas.sales_retail import RetailSaleCreate, RetailSaleUpdate


def create_sale(db: Session, data: RetailSaleCreate) -> SalesRetail:
    sale = SalesRetail(
        store_id=data.store_id,
        sku_id=data.sku_id,
        qty=data.qty,
        amount=data.amount,
        sold_at=data.sold_at,
        external_id=data.external_id,
        feed_batch_id=data.feed_batch_id,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def update_sale(db: Session, sale: SalesRetail, data: RetailSaleUpdate) -> SalesRetail:
    if data.qty is not None:
        if data.qty <= 0:
            raise HTTPException(status_code=400, detail={"code": "qty_invalid", "detail": "qty must be > 0"})
        sale.qty = data.qty
    if data.amount is not None:
        if data.amount < 0:
            raise HTTPException(status_code=400, detail={"code": "amount_invalid", "detail": "amount must be >= 0"})
        sale.amount = data.amount
    if data.sold_at is not None:
        sale.sold_at = data.sold_at
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, sale: SalesRetail) -> None:
    db.delete(sale)
    db.commit()


def import_sales(db: Session, items: list[RetailSaleCreate]) -> tuple[int, list[str]]:
    """Batch import sales; skip duplicates by external_id."""

    skipped: list[str] = []
    created = 0
    seen: set[str] = set()
    for item in items:
        if item.external_id:
            if item.external_id in seen:
                skipped.append(item.external_id)
                continue
            exists = db.scalar(select(SalesRetail.id).where(SalesRetail.external_id == item.external_id))
            if exists:
                skipped.append(item.external_id)
                seen.add(item.external_id)
                continue
            seen.add(item.external_id)
        sale = SalesRetail(
            store_id=item.store_id,
            sku_id=item.sku_id,
            qty=item.qty,
            amount=item.amount,
            sold_at=item.sold_at,
            external_id=item.external_id,
            feed_batch_id=item.feed_batch_id,
        )
        db.add(sale)
        created += 1
    db.commit()
    return created, skipped


__all__ = ["create_sale", "update_sale", "delete_sale", "import_sales"]
