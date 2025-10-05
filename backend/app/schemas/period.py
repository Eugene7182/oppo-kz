"""Schemas for closed periods management."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.period import ClosedScope


class PeriodCloseRequest(BaseModel):
    """Запрос на закрытие периода."""

    from_date: date
    to_date: date
    scope: ClosedScope
    scope_id: str | None = Field(default=None, max_length=36)


class PeriodOut(BaseModel):
    """Выходная модель периода."""

    id: str
    scope: ClosedScope
    scope_id: str | None
    from_date: date
    to_date: date
    created_by: str | None
    created_at: datetime


class PeriodList(BaseModel):
    """Список закрытых периодов."""

    items: list[PeriodOut]


__all__ = ["PeriodCloseRequest", "PeriodOut", "PeriodList"]
