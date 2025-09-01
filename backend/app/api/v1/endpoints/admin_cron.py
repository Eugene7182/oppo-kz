from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_power

router = APIRouter(prefix="/admin/cron", tags=["admin"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.post("/close-day")
def close_day(d: str | None = Query(None), db: Session = Depends(get_db), _: None = Depends(require_power)):
    run_date = date.fromisoformat(d) if d else date.today()
    if not _has(db, "promoter_daily_checkins") or not _has(db, "users"):
        raise HTTPException(status_code=503, detail="tables missing")
    # get all promoters
    users = db.execute(text("select username from users where role='promoter'")).mappings().all()
    cnt=0
    for u in users:
        username = u["username"]
        # check any sales
        has = False
        if _has(db, "sales_daily"):
            r = db.execute(text("select 1 from sales_daily where promoter=:p and date=:d limit 1"), {"p": username, "d": run_date}).first()
            has = bool(r)
        if not has:
            # insert zero-day if not exists
            db.execute(text("""
                insert into promoter_daily_checkins(promoter, date, has_sales)
                values (:p, :d, false)
                on conflict (promoter, date) do nothing
            """), {"p": username, "d": run_date})
            cnt += 1
    db.commit()
    return {"ok": True, "zeros_added": cnt, "date": run_date.isoformat()}
