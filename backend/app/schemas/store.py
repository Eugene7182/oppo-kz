# backend/app/schemas/store.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional

class StoreIn(BaseModel):
    """Входная модель для создания/обновления магазина."""
    name: str
    network_id: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    coefficient_letter: Optional[str] = None  # отдельная сущность в аналитике, но допустим поле
    coefficient_numeric: Optional[float] = None

class StoreOut(StoreIn):
    """Выходная модель (чтение)."""
    model_config = ConfigDict(from_attributes=True)
    id: str


class StoreBase(BaseModel):
    """Базовые поля магазина."""

    network_id: str
    region_id: str
    code: str
    name: str
    address: str | None = None
    active: bool | None = True


class StoreCreate(StoreBase):
    """Создание магазина."""
    pass


class StoreUpdate(BaseModel):
    """Обновление магазина."""

    network_id: str | None = None
    region_id: str | None = None
    code: str | None = None
    name: str | None = None
    address: str | None = None
    active: bool | None = None


class StoreRead(StoreBase):
    """Чтение магазина."""

    model_config = ConfigDict(from_attributes=True)
    id: str


__all__ = [
    "StoreIn",
    "StoreOut",
    "StoreCreate",
    "StoreUpdate",
    "StoreRead",
]
