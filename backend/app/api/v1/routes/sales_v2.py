"""Sales API v2 implementing optimistic locking and corrections."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.authz import require_roles
from app.core.security import get_current_user, get_db
from app.models.period import ClosedPeriod, ClosedScope
from app.models.sale import Sale, SaleCorrection, SaleRevision, SaleStatus
from app.models.store import Store
from app.models.user import User, UserRole
from app.schemas.sale import (
    SaleCorrectionCreate,
    SaleCorrectionOut,
    SaleCreate,
    SaleList,
    SaleOut,
    SaleUpdate,
)

router = APIRouter(prefix="/sales", tags=["sales"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _fetch_store(db: Session, store_id: str) -> Store:
    store = db.query(Store).filter(Store.id == store_id).one_or_none()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return store


def _ensure_period_open(db: Session, store: Store, sale_date) -> None:
    locked = (
        db.query(ClosedPeriod)
        .filter(
            ClosedPeriod.from_date <= sale_date,
            ClosedPeriod.to_date >= sale_date,
            or_(
                ClosedPeriod.scope == ClosedScope.country,
                and_(ClosedPeriod.scope == ClosedScope.region, ClosedPeriod.scope_id == store.region_id),
                and_(ClosedPeriod.scope == ClosedScope.store, ClosedPeriod.scope_id == store.id),
            ),
        )
        .first()
    )
    if locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Period is locked", "code": "locked_period"},
        )


def _ensure_sale_permissions(sale: Sale, current: User) -> None:
    if current.role in {UserRole.admin, UserRole.office}:
        return
    if current.role == UserRole.promoter and sale.promoter_id == current.id:
        return
    if current.role == UserRole.supervisor and current.region_id:
        store_region = sale.store.region_id if sale.store else None
        if store_region == current.region_id:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def _load_corrections(db: Session, sale_ids: list[str]) -> dict[str, tuple[int, Decimal]]:
    if not sale_ids:
        return {}
    rows = (
        db.query(
            SaleCorrection.sale_id,
            func.coalesce(func.sum(SaleCorrection.delta_qty), 0),
            func.coalesce(func.sum(SaleCorrection.delta_price), 0),
        )
        .filter(SaleCorrection.sale_id.in_(sale_ids))
        .group_by(SaleCorrection.sale_id)
        .all()
    )
    return {row[0]: (int(row[1] or 0), Decimal(row[2] or 0)) for row in rows}


def _serialize_sale(sale: Sale, delta_qty: int, delta_price: Decimal) -> SaleOut:
    fact_qty = sale.qty + delta_qty
    base_revenue = (sale.price or Decimal(0)) * sale.qty
    fact_revenue = base_revenue + delta_price
    return SaleOut(
        id=sale.id,
        promoter_id=sale.promoter_id,
        store_id=sale.store_id,
        sku_id=sale.sku_id,
        date=sale.date,
        qty=sale.qty,
        price=sale.price,
        status=sale.status,
        version=sale.version,
        locked=bool(sale.locked_at),
        corrected=bool(delta_qty) or bool(delta_price),
        fact_qty=fact_qty,
        fact_revenue=fact_revenue,
        locked_at=sale.locked_at,
    )


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.promoter])),
) -> SaleOut:
    existing = db.get(Sale, payload.sale_id)
    if existing:
        _ensure_sale_permissions(existing, current)
        corrections = _load_corrections(db, [existing.id])
        delta_qty, delta_price = corrections.get(existing.id, (0, Decimal(0)))
        return _serialize_sale(existing, delta_qty, delta_price)

    store = _fetch_store(db, payload.store_id)
    _ensure_period_open(db, store, payload.date)

    sale = Sale(
        id=payload.sale_id,
        promoter_id=current.id,
        store_id=payload.store_id,
        sku_id=payload.sku_id,
        date=payload.date,
        qty=payload.qty,
        price=payload.price,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return _serialize_sale(sale, 0, Decimal(0))


@router.patch("/{sale_id}", response_model=SaleOut)
def update_sale(
    sale_id: str,
    payload: SaleUpdate,
    if_match: str | None = Header(default=None, alias="If-Match"),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> SaleOut:
    if not if_match:
        raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail="If-Match header required")
    sale = db.query(Sale).options(joinedload(Sale.store)).filter(Sale.id == sale_id).one_or_none()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    _ensure_sale_permissions(sale, current)
    if str(sale.version) != if_match:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "version_conflict"})
    if sale.locked_at:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "locked_period"})

    data = payload.model_dump(exclude_unset=True)
    reason = data.pop("reason", None)
    new_date = data.get("date", sale.date)
    _ensure_period_open(db, sale.store, new_date)

    before = {
        "date": sale.date.isoformat(),
        "qty": sale.qty,
        "price": str(sale.price) if sale.price is not None else None,
    }

    if "date" in data:
        sale.date = data["date"]
    if "qty" in data:
        sale.qty = data["qty"]
    if "price" in data:
        sale.price = data["price"]

    sale.version += 1
    sale.updated_at = _utcnow()

    revision = SaleRevision(
        sale_id=sale.id,
        changed_by=current.id,
        before_json=before,
        after_json={
            "date": sale.date.isoformat(),
            "qty": sale.qty,
            "price": str(sale.price) if sale.price is not None else None,
        },
        reason=reason,
        changed_at=_utcnow(),
    )
    db.add(revision)
    db.commit()
    db.refresh(sale)
    corrections = _load_corrections(db, [sale.id])
    delta_qty, delta_price = corrections.get(sale.id, (0, Decimal(0)))
    return _serialize_sale(sale, delta_qty, delta_price)


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Response:
    sale = db.query(Sale).options(joinedload(Sale.store)).filter(Sale.id == sale_id).one_or_none()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    _ensure_sale_permissions(sale, current)
    if sale.locked_at:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "locked_period"})
    _ensure_period_open(db, sale.store, sale.date)
    sale.status = SaleStatus.deleted
    sale.updated_at = _utcnow()
    db.add(sale)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{sale_id}/corrections", response_model=SaleCorrectionOut, status_code=status.HTTP_201_CREATED)
def create_correction(
    sale_id: str,
    payload: SaleCorrectionCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> SaleCorrection:
    role = UserRole(current.role)
    if role not in {UserRole.promoter, UserRole.supervisor, UserRole.office, UserRole.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    sale = (
        db.query(Sale)
        .options(joinedload(Sale.store))
        .filter(Sale.id == sale_id)
        .one_or_none()
    )
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    if not sale.locked_at:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sale must be locked")
    _ensure_sale_permissions(sale, current)
    if role == UserRole.promoter and sale.promoter_id != current.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    correction = SaleCorrection(
        sale_id=sale.id,
        created_by=current.id,
        delta_qty=payload.delta_qty,
        delta_price=payload.delta_price,
        reason=payload.reason,
        created_at=_utcnow(),
    )
    db.add(correction)
    db.commit()
    db.refresh(correction)
    return correction


@router.get("", response_model=SaleList)
def list_sales(
    promoter_id: str | None = Query(default=None),
    region_id: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> SaleList:
    query = db.query(Sale).options(joinedload(Sale.store)).join(Store, Store.id == Sale.store_id)

    if promoter_id:
        query = query.filter(Sale.promoter_id == promoter_id)
    if region_id:
        query = query.filter(Store.region_id == region_id)
    if date_from:
        query = query.filter(Sale.date >= date_from.date())
    if date_to:
        query = query.filter(Sale.date <= date_to.date())

    if current.role == UserRole.promoter:
        query = query.filter(Sale.promoter_id == current.id)
    elif current.role == UserRole.supervisor and current.region_id:
        query = query.filter(Store.region_id == current.region_id)

    sales = query.order_by(Sale.date.desc()).all()
    corrections = _load_corrections(db, [sale.id for sale in sales])
    items = []
    for sale in sales:
        delta_qty, delta_price = corrections.get(sale.id, (0, Decimal(0)))
        items.append(_serialize_sale(sale, delta_qty, delta_price))
    return SaleList(items=items)
