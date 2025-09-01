from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from ....core.security import get_current_user

router = APIRouter(prefix="/anomalies", tags=["anomalies"])

@router.get("")
def list_anomalies(store: str | None = None, sku: str | None = None, from_date: str | None = None, to_date: str | None = None, user=Depends(get_current_user)):
    # MVP: статический набор примеров
    data = [
        {"id": 1, "type": "price_spike", "sku": "OPPO-RENO10", "store": "A01", "date": "2025-08-25", "score": 0.92},
        {"id": 2, "type": "sales_drop", "sku": "OPPO-A1K", "store": "A02", "date": "2025-08-28", "score": 0.87},
    ]
    # простая фильтрация
    if store: data = [x for x in data if x["store"] == store]
    if sku: data = [x for x in data if x["sku"] == sku]
    return data
