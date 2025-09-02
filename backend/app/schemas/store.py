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
