"""Bonus scheme schemas."""
from __future__ import annotations

from datetime import date, datetime
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.bonus import BonusSchemeStatus, BonusSelectorType


class BonusRuleCreate(BaseModel):
    """Правило бонусной схемы при создании."""

    selector_type: BonusSelectorType
    selector_value: str | None = Field(default=None, max_length=255)
    amount: Decimal = Field(gt=0)
    conditions: dict[str, Any] | None = None


class BonusSchemeCreate(BaseModel):
    """Создание бонусной схемы."""

    network_id: str
    valid_from: date
    valid_to: date | None = None
    rules: list[BonusRuleCreate]


class BonusRuleOut(BaseModel):
    """DTO правила бонусов."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    selector_type: BonusSelectorType
    selector_value: str | None
    amount: Decimal
    conditions_json: dict[str, Any] | None


class BonusSchemeOut(BaseModel):
    """DTO бонусной схемы."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    network_id: str
    valid_from: date
    valid_to: date | None
    status: BonusSchemeStatus
    rules: list[BonusRuleOut]
    created_at: datetime
    updated_at: datetime


__all__ = [
    "BonusRuleCreate",
    "BonusSchemeCreate",
    "BonusRuleOut",
    "BonusSchemeOut",
]
