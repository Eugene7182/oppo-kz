from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user, require_office_or_supervisor_or_admin as require_power
from app.kpi.service import kpi_city, kpi_office, month_start

router = APIRouter(prefix="/kpi", tags=["kpi"])

@router.get("/city")
def kpi_for_city(city: str = Query(None), month: str | None = Query(None), db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_power)):
    c = city or getattr(user, "city_code", None)
    return kpi_city(db, c or "UNKNOWN", month)

@router.get("/office")
def kpi_for_office(month: str | None = Query(None), db: Session = Depends(get_db), _: None = Depends(require_power)):
    return kpi_office(db, month)
