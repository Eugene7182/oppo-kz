from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_power, get_current_user
from app.plans.service import set_plan as svc_set, get_plans_for_city as svc_city, get_plans_all as svc_all

router = APIRouter(prefix="/plans", tags=["plans"])

@router.post("")
def set_plan(payload: dict, db: Session = Depends(get_db), _: None = Depends(require_power), user = Depends(get_current_user)):
    store_id = payload.get("store_id"); month = payload.get("month"); plan_qty = payload.get("plan_qty")
    if not store_id or not month or plan_qty is None:
        raise HTTPException(status_code=400, detail="store_id, month, plan_qty required")
    return svc_set(db, store_id, month, int(plan_qty), getattr(user, "username", None))

@router.get("/city")
def plans_city(city: str = Query(...), month: str = Query(...), db: Session = Depends(get_db), _: None = Depends(require_power)):
    return svc_city(db, city, month)

@router.get("/all")
def plans_all(month: str = Query(...), db: Session = Depends(get_db), _: None = Depends(require_power)):
    return svc_all(db, month)
