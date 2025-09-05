from __future__ import annotations

"""Business logic for promoter sales."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sales_promoters import SalesPromoter
from app.models.user import User, UserRole
from app.schemas.sales_promoters import PromoterSaleCreate, PromoterSaleUpdate


def create_sale(db: Session, data: PromoterSaleCreate, current_user: User) -> SalesPromoter:
    """Create promoter sale. promoter_id defaults to current user."""

    promoter_id = data.promoter_id or current_user.id
    if current_user.role == UserRole.promoter and promoter_id != current_user.id:
        raise HTTPException(status_code=403, detail={"code": "forbidden", "detail": "Cannot create for other promoter"})
    sale = SalesPromoter(
        store_id=data.store_id,
        sku_id=data.sku_id,
        qty=data.qty,
        amount=data.amount,
        sold_at=data.sold_at,
        promoter_id=promoter_id,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def update_sale(db: Session, sale: SalesPromoter, data: PromoterSaleUpdate) -> SalesPromoter:
    """Update promoter sale if not approved."""

    if sale.approved_by_office:
        raise HTTPException(
            status_code=409,
            detail={"code": "sale_approved_locked", "detail": "Approved sale cannot be changed"},
        )
    if data.qty is not None:
        sale.qty = data.qty
    if data.amount is not None:
        sale.amount = data.amount
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, sale: SalesPromoter) -> None:
    """Delete sale if not approved."""

    if sale.approved_by_office:
        raise HTTPException(
            status_code=409,
            detail={"code": "sale_approved_locked", "detail": "Approved sale cannot be deleted"},
        )
    db.delete(sale)
    db.commit()


def approve_sale(db: Session, sale: SalesPromoter, user: User) -> SalesPromoter:
    """Mark sale approved by office."""

    sale.approved_by_office = True
    sale.approved_at = datetime.now(timezone.utc)
    sale.approved_by_user_id = user.id
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def unapprove_sale(db: Session, sale: SalesPromoter) -> SalesPromoter:
    """Revoke approval."""

    sale.approved_by_office = False
    sale.approved_at = None
    sale.approved_by_user_id = None
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


__all__ = [
    "create_sale",
    "update_sale",
    "delete_sale",
    "approve_sale",
    "unapprove_sale",
]
