from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ReconciliationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: str
    status: Optional[str] = None
    created_at: Optional[datetime] = None
