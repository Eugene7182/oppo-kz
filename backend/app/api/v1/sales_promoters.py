from __future__ import annotations

"""API for promoter sales."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, rbac_required
from app.db.session import get_db
from app.models.sales_promoters import SalesPromoter
from app.models.user import User, UserRole
from app.schemas.sales_promoters import (
    PromoterSaleCreate,
    PromoterSaleRead,
    PromoterSaleUpdate,
)
from app.services.sales_filters import build_promoter_query
from app.services.sales_promoters import (
    approve_sale,
    create_sale,
    delete_sale,
    unapprove_sale,
    update_sale,
)

router = APIRouter(prefix="/sales/promoters", tags=["sales_promoters"])


@router.get("", response_model=dict)
def list_sales(
    date_from: date | None = None,
    date_to: date | None = None,
    store_id: str | None = None,
    sku_id: str | None = None,
    promoter_id: str | None = None,
    approved: bool | None = None,
    network_id: str | None = None,
    region_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    q: str | None = None,  # игнорируется, зарезервировано
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Список продаж промоутеров."""

    limit = min(limit, 200)
    filters = {
        "date_from": date_from,
        "date_to": date_to,
        "store_id": store_id,
        "sku_id": sku_id,
        "promoter_id": promoter_id,
        "approved": approved,
        "network_id": network_id,
        "region_id": region_id,
    }
    if current_user.role == UserRole.promoter:
        filters["promoter_id"] = current_user.id
    stmt = build_promoter_query(db, filters)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(
        stmt.order_by(SalesPromoter.sold_at.desc()).offset(offset).limit(limit)
    ).all()
    items = [PromoterSaleRead.model_validate(r) for r in rows]
    return {"items": items, "total": total}


_allowed_create = rbac_required(
    [UserRole.promoter, UserRole.supervisor, UserRole.office, UserRole.admin]
)
_admin_office = rbac_required([UserRole.admin, UserRole.office])


@router.post(
    "",
    dependencies=[Depends(_allowed_create)],
    response_model=PromoterSaleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sale_endpoint(
    data: PromoterSaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromoterSaleRead:
    sale = create_sale(db, data, current_user)
    return PromoterSaleRead.model_validate(sale)


@router.put("/{sale_id}", response_model=PromoterSaleRead)
def update_sale_endpoint(
    sale_id: str,
    data: PromoterSaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromoterSaleRead:
    sale = db.get(SalesPromoter, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail={"code": "sale_not_found", "detail": "Not found"})
    if sale.approved_by_office:
        raise HTTPException(
            status_code=409,
            detail={"code": "sale_approved_locked", "detail": "Approved sale cannot be changed"},
        )
    if current_user.role not in [UserRole.admin, UserRole.office] and sale.promoter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": "forbidden", "detail": "Not enough permissions"},
        )
    sale = update_sale(db, sale, data)
    return PromoterSaleRead.model_validate(sale)


@router.delete(
    "/{sale_id}", dependencies=[Depends(_admin_office)], response_model=PromoterSaleRead
)
def delete_sale_endpoint(sale_id: str, db: Session = Depends(get_db)) -> PromoterSaleRead:
    sale = db.get(SalesPromoter, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail={"code": "sale_not_found", "detail": "Not found"})
    if sale.approved_by_office:
        raise HTTPException(
            status_code=409,
            detail={"code": "sale_approved_locked", "detail": "Approved sale cannot be deleted"},
        )
    data = PromoterSaleRead.model_validate(sale)
    delete_sale(db, sale)
    return data


@router.post(
    "/{sale_id}/approve",
    dependencies=[Depends(_admin_office)],
    response_model=PromoterSaleRead,
)
def approve_sale_endpoint(
    sale_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> PromoterSaleRead:
    sale = db.get(SalesPromoter, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail={"code": "sale_not_found", "detail": "Not found"})
    sale = approve_sale(db, sale, current_user)
    return PromoterSaleRead.model_validate(sale)


@router.post(
    "/{sale_id}/unapprove",
    dependencies=[Depends(_admin_office)],
    response_model=PromoterSaleRead,
)
def unapprove_sale_endpoint(sale_id: str, db: Session = Depends(get_db)) -> PromoterSaleRead:
    sale = db.get(SalesPromoter, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail={"code": "sale_not_found", "detail": "Not found"})
    sale = unapprove_sale(db, sale)
    return PromoterSaleRead.model_validate(sale)


__all__ = ["router"]
