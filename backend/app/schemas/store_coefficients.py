from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class StoreCoefficientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: str
    store_id: Optional[str] = None
    letter: Optional[str] = None
    numeric: Optional[float] = None
    effective_from: Optional[date] = None


class StoreCoefficientIn(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    store_id: int
    code: str
    value: Optional[float] = None
    note: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

class StoreCoefficientUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    store_id: Optional[int] = None
    code: Optional[str] = None
    value: Optional[float] = None
    note: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
