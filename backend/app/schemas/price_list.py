from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PriceListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: str
    sku_id: Optional[str] = None
    price: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
