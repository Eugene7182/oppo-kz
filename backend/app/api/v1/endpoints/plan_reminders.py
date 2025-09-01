from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from app.api.v1.deps import get_db, get_current_user, require_supervisor

router = APIRouter(prefix="/plans/reminders", tags=["plans"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.get("/supervisor")
def remind_super(city: str | None = Query(None), month: str | None = Query(None), db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_supervisor)):
    if not month:
        month = date.today().replace(day=1).isoformat()
    u_city = getattr(user, "city_code", None)
    if not city:
        city = u_city
    if not city or not _has(db, "stores"):
        return {"needs_plan": False, "missing_count": 0}
    # stores in city
    stores = db.execute(text("select store_id from stores where city_code=:c"), {"c": city}).mappings().all()
    store_ids = [r["store_id"] for r in stores]
    if not store_ids:
        return {"needs_plan": False, "missing_count": 0}
    missing = 0
    if _has(db, "plans_store_month"):
        q = db.execute(text("""
           select s.store_id, p.store_id as has_plan
           from (select unnest(:ids) as store_id) s
           left join plans_store_month p on p.store_id = s.store_id and p.month=:m
        """), {"ids": store_ids, "m": month}).mappings().all()
        missing = sum(1 for r in q if r["has_plan"] is None)
    return {"needs_plan": missing > 0, "missing_count": int(missing), "city": city, "month": month}
