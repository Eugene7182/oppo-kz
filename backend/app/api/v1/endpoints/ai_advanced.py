from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_power
from app.ai.abcxyz import classify_abcxyz
from app.ai.forecast import forecast_sales

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/classify/abcxyz")
def ai_abcxyz(days: int = Query(60, ge=14, le=365), db: Session = Depends(get_db), _: None = Depends(require_power)):
    return classify_abcxyz(db, days)

@router.get("/forecast/sales")
def ai_forecast(group_by: str = Query("total"), horizon_days: int = Query(30, ge=7, le=120),
                db: Session = Depends(get_db), _: None = Depends(require_power)):
    return forecast_sales(db, group_by, horizon_days)
