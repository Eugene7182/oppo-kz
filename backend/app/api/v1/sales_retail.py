from __future__ import annotations

"""API for retail sales."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, rbac_required
from app.db.session import get_db
from app.feature_flags.deps import check_feature
from app.models.sales_retail import SalesRetail
from app.models.user import UserRole
from app.schemas.sales_retail import (
    RetailSaleCreate,
    RetailSaleRead,
    RetailSaleUpdate,
    RetailSalesImport,
)
from app.services.sales_filters import build_retail_query
from app.services.sales_retail import create_sale, delete_sale, import_sales, update_sale

router = APIRouter(prefix="/sales/retail", tags=["sales_retail"])


@router.get("", response_model=dict)
def list_sales(
    date_from: date | None = None,
    date_to: date | None = None,
    store_id: str | None = None,
    sku_id: str | None = None,
    feed_batch_id: str | None = None,
    network_id: str | None = None,
    region_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    """Список продаж из сетей."""

    limit = min(limit, 200)
    filters = {
        "date_from": date_from,
        "date_to": date_to,
        "store_id": store_id,
        "sku_id": sku_id,
        "feed_batch_id": feed_batch_id,
        "network_id": network_id,
        "region_id": region_id,
    }
    stmt = build_retail_query(db, filters)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(SalesRetail.sold_at.desc()).offset(offset).limit(limit)).all()
    items = [RetailSaleRead.model_validate(r) for r in rows]
    return {"items": items, "total": total}


_admin_office = rbac_required([UserRole.admin, UserRole.office])


@router.post(
    "",
    dependencies=[Depends(_admin_office)],
    response_model=RetailSaleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sale_endpoint(data: RetailSaleCreate, db: Session = Depends(get_db)) -> RetailSaleRead:
    sale = create_sale(db, data)
    return RetailSaleRead.model_validate(sale)


@router.put(
    "/{sale_id}", dependencies=[Depends(_admin_office)], response_model=RetailSaleRead
)
def update_sale_endpoint(
    sale_id: str,
    data: RetailSaleUpdate,
    db: Session = Depends(get_db),
) -> RetailSaleRead:
    sale = db.get(SalesRetail, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail={"code": "sale_not_found", "detail": "Not found"})
    sale = update_sale(db, sale, data)
    return RetailSaleRead.model_validate(sale)


@router.delete(
    "/{sale_id}", dependencies=[Depends(_admin_office)], response_model=RetailSaleRead
)
def delete_sale_endpoint(sale_id: str, db: Session = Depends(get_db)) -> RetailSaleRead:
    sale = db.get(SalesRetail, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail={"code": "sale_not_found", "detail": "Not found"})
    data = RetailSaleRead.model_validate(sale)
    delete_sale(db, sale)
    return data


@router.post(
    "/import",
    dependencies=[Depends(_admin_office), Depends(check_feature("ENABLE_IMPORTS"))],
    response_model=dict,
)
def import_sales_endpoint(
    payload: RetailSalesImport, db: Session = Depends(get_db)
) -> dict:
    created, skipped = import_sales(db, payload.items)
    return {"created": created, "skipped": skipped}


__all__ = ["router"]
