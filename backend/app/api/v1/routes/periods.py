"""Closed periods management endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.authz import require_roles
from app.core.security import get_current_user, get_db
from app.models.period import ClosedPeriod, ClosedScope
from app.models.sale import Sale
from app.models.store import Store
from app.models.user import User, UserRole
from app.schemas.period import PeriodCloseRequest, PeriodList, PeriodOut

router = APIRouter(prefix="/periods", tags=["periods"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _apply_lock(db: Session, period: ClosedPeriod) -> None:
    """Отмечает связанные продажи как заблокированные."""

    query = db.query(Sale)
    if period.scope == ClosedScope.country:
        pass
    elif period.scope == ClosedScope.region:
        stores = db.query(Store.id).filter(Store.region_id == period.scope_id).subquery()
        query = query.filter(Sale.store_id.in_(stores))
    elif period.scope == ClosedScope.store:
        query = query.filter(Sale.store_id == period.scope_id)

    query = query.filter(Sale.date >= period.from_date, Sale.date <= period.to_date)
    query.update({Sale.locked_at: _utcnow()}, synchronize_session=False)


@router.post("/close", response_model=PeriodOut, status_code=status.HTTP_201_CREATED)
def close_period(
    payload: PeriodCloseRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin, UserRole.office])),
) -> ClosedPeriod:
    if payload.from_date > payload.to_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="from_date must be before to_date")
    if payload.scope != ClosedScope.country and not payload.scope_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="scope_id required")

    existing = (
        db.query(ClosedPeriod)
        .filter(
            ClosedPeriod.scope == payload.scope,
            ClosedPeriod.scope_id == payload.scope_id,
            ClosedPeriod.from_date <= payload.to_date,
            ClosedPeriod.to_date >= payload.from_date,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Period overlap")

    period = ClosedPeriod(
        scope=payload.scope,
        scope_id=payload.scope_id,
        from_date=payload.from_date,
        to_date=payload.to_date,
        created_by=current.id,
        created_at=_utcnow(),
    )
    db.add(period)
    db.flush()
    _apply_lock(db, period)
    db.commit()
    db.refresh(period)
    return period


@router.get("/closed", response_model=PeriodList)
def list_periods(
    scope: ClosedScope | None = Query(default=None),
    scope_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> PeriodList:
    query = db.query(ClosedPeriod)
    if scope:
        query = query.filter(ClosedPeriod.scope == scope)
    if scope_id:
        query = query.filter(ClosedPeriod.scope_id == scope_id)

    if current.role == UserRole.supervisor and current.region_id:
        query = query.filter(
            or_(
                ClosedPeriod.scope == ClosedScope.country,
                and_(ClosedPeriod.scope == ClosedScope.region, ClosedPeriod.scope_id == current.region_id),
            )
        )
    if current.role == UserRole.promoter:
        # promoters can only see country level periods
        query = query.filter(ClosedPeriod.scope == ClosedScope.country)

    periods = query.order_by(ClosedPeriod.from_date.desc()).all()
    return PeriodList(items=periods)
