"""Bonus scheme endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authz import require_roles
from app.core.security import get_db
from app.models.bonus import BonusScheme, BonusSchemeStatus, BonusRule
from app.models.user import User, UserRole
from app.schemas.bonus_scheme import BonusSchemeCreate, BonusSchemeOut

router = APIRouter(prefix="/bonus-schemes", tags=["bonus_schemes"])


@router.get("", response_model=list[BonusSchemeOut])
def list_bonus_schemes(
    network_id: str | None = Query(default=None),
    status_filter: BonusSchemeStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[BonusScheme]:
    """Список бонусных схем по сети."""

    query = db.query(BonusScheme).order_by(BonusScheme.valid_from.desc())
    if network_id:
        query = query.filter(BonusScheme.network_id == network_id)
    if status_filter:
        query = query.filter(BonusScheme.status == status_filter)
    return query.all()


@router.post("", response_model=BonusSchemeOut, status_code=status.HTTP_201_CREATED)
def create_bonus_scheme(
    payload: BonusSchemeCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin])),
) -> BonusScheme:
    """Создать черновик бонусной схемы."""

    if not payload.rules:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one rule required")

    scheme = BonusScheme(
        network_id=payload.network_id,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        status=BonusSchemeStatus.draft,
    )
    db.add(scheme)
    db.flush()
    for rule in payload.rules:
        db.add(
            BonusRule(
                scheme_id=scheme.id,
                selector_type=rule.selector_type,
                selector_value=rule.selector_value,
                amount=rule.amount,
                conditions_json=rule.conditions,
            )
        )
    db.commit()
    db.refresh(scheme)
    return scheme


@router.post("/{scheme_id}/publish", response_model=BonusSchemeOut)
def publish_bonus_scheme(
    scheme_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin])),
) -> BonusScheme:
    """Перевести бонусную схему в статус published."""

    scheme = db.query(BonusScheme).filter(BonusScheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus scheme not found")
    if scheme.status == BonusSchemeStatus.published:
        return scheme
    scheme.status = BonusSchemeStatus.published
    scheme.updated_at = datetime.now(timezone.utc)
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    return scheme


__all__ = ["router"]
