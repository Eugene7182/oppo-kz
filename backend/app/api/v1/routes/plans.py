"""Promoter monthly plans endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authz import require_roles
from app.core.security import get_current_user, get_db
from app.models.plan import PlanAudit, PlanPromoterMonth
from app.models.store import Store
from app.models.user import User, UserRole
from app.schemas.plan import PlanList, PlanPatch, PlanPromoterMonthItem, PlanPromoterMonthOut

router = APIRouter(prefix="/plans/promoter-month", tags=["plans"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(plan: PlanPromoterMonth) -> PlanPromoterMonthOut:
    return PlanPromoterMonthOut(
        id=plan.id,
        period_ym=plan.period_ym,
        promoter_id=plan.promoter_id,
        store_id=plan.store_id,
        target_units=plan.target_units,
        target_revenue=plan.target_revenue,
        source=plan.source,
        version=plan.version,
        updated_by=plan.updated_by,
        updated_at=plan.updated_at,
    )


@router.post("/bulk", response_model=PlanList, status_code=status.HTTP_201_CREATED)
def bulk_upsert(
    items: list[PlanPromoterMonthItem],
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin, UserRole.office, UserRole.supervisor])),
) -> PlanList:
    results: list[PlanPromoterMonth] = []
    for item in items:
        if current.role == UserRole.supervisor:
            if current.region_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supervisor must have region")
            # ensure store belongs to supervisor region if provided
            if item.store_id:
                store = db.query(Store).filter(Store.id == item.store_id).one_or_none()
                if not store or store.region_id != current.region_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Store outside supervisor region")
        plan = (
            db.query(PlanPromoterMonth)
            .filter(
                PlanPromoterMonth.period_ym == item.period_ym,
                PlanPromoterMonth.promoter_id == item.promoter_id,
                PlanPromoterMonth.store_id == item.store_id,
            )
            .one_or_none()
        )
        if plan:
            before = {
                "target_units": plan.target_units,
                "target_revenue": str(plan.target_revenue),
            }
            plan.target_units = item.target_units
            plan.target_revenue = item.target_revenue
            plan.source = item.source
            plan.version += 1
            plan.updated_by = current.id
            plan.updated_at = _utcnow()
            audit = PlanAudit(
                plan_id=plan.id,
                before_json=before,
                after_json={"target_units": plan.target_units, "target_revenue": str(plan.target_revenue)},
                reason=item.reason,
                updated_by=current.id,
                updated_at=_utcnow(),
            )
            db.add(audit)
        else:
            plan = PlanPromoterMonth(
                period_ym=item.period_ym,
                promoter_id=item.promoter_id,
                store_id=item.store_id,
                target_units=item.target_units,
                target_revenue=item.target_revenue,
                source=item.source,
                updated_by=current.id,
                updated_at=_utcnow(),
            )
            db.add(plan)
        results.append(plan)
    db.commit()
    for plan in results:
        db.refresh(plan)
    return PlanList(items=[_serialize(plan) for plan in results])


@router.patch("/{plan_id}", response_model=PlanPromoterMonthOut)
def patch_plan(
    plan_id: str,
    payload: PlanPatch,
    if_match: str | None = Header(default=None, alias="If-Match"),
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin, UserRole.office, UserRole.supervisor])),
) -> PlanPromoterMonthOut:
    if not if_match:
        raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail="If-Match header required")
    plan = db.query(PlanPromoterMonth).filter(PlanPromoterMonth.id == plan_id).one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    if str(plan.version) != if_match:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "version_conflict"})
    if current.role == UserRole.supervisor and current.region_id:
        if plan.store_id:
            store = db.query(Store).filter(Store.id == plan.store_id).one_or_none()
            if not store or store.region_id != current.region_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Store outside supervisor region")

    data = payload.model_dump(exclude_unset=True)
    before = {
        "target_units": plan.target_units,
        "target_revenue": str(plan.target_revenue),
    }
    if "target_units" in data:
        plan.target_units = data["target_units"]
    if "target_revenue" in data:
        plan.target_revenue = data["target_revenue"]
    plan.version += 1
    plan.updated_by = current.id
    plan.updated_at = _utcnow()
    audit = PlanAudit(
        plan_id=plan.id,
        before_json=before,
        after_json={
            "target_units": plan.target_units,
            "target_revenue": str(plan.target_revenue),
        },
        reason=data.get("reason"),
        updated_by=current.id,
        updated_at=_utcnow(),
    )
    db.add(audit)
    db.commit()
    db.refresh(plan)
    return _serialize(plan)


@router.get("", response_model=PlanList)
def list_plans(
    promoter_id: str | None = Query(default=None),
    region_id: str | None = Query(default=None),
    period: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> PlanList:
    query = db.query(PlanPromoterMonth)
    if promoter_id:
        query = query.filter(PlanPromoterMonth.promoter_id == promoter_id)
    if period:
        query = query.filter(PlanPromoterMonth.period_ym == period)
    if region_id:
        stores = db.query(Store.id).filter(Store.region_id == region_id).subquery()
        query = query.filter(
            PlanPromoterMonth.store_id.is_(None) | PlanPromoterMonth.store_id.in_(stores)
        )

    if current.role == UserRole.supervisor and current.region_id:
        stores = db.query(Store.id).filter(Store.region_id == current.region_id).subquery()
        query = query.filter(
            PlanPromoterMonth.store_id.is_(None) | PlanPromoterMonth.store_id.in_(stores)
        )
    if current.role == UserRole.promoter:
        query = query.filter(PlanPromoterMonth.promoter_id == current.id)

    plans = query.order_by(PlanPromoterMonth.period_ym.desc()).all()
    return PlanList(items=[_serialize(plan) for plan in plans])
