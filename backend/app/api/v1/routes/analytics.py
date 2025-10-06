"""Analytics endpoints."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.authz import require_roles
from app.core.security import get_db
from app.models.user import UserRole
from app.schemas.analytics import SalesPerformanceOut
from app.services.analytics import SalesAnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sales/summary", response_model=SalesPerformanceOut)
def sales_summary(
    as_of: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles([UserRole.admin, UserRole.office, UserRole.supervisor])),
) -> SalesPerformanceOut:
    """Возвращает агрегированные метрики продаж."""

    service = SalesAnalyticsService(db)
    result = service.compute(as_of or date.today())
    return SalesPerformanceOut.model_validate(result)


__all__ = ["router"]
