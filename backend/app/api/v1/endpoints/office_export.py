from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_office

router = APIRouter(prefix="/office", tags=["office"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _week_start(d: date | None = None) -> date:
    d = d or date.today()
    return d - timedelta(days=d.weekday())

@router.get("/compliance/export.csv")
def export_compliance_csv(week_start: str | None = Query(None), db: Session = Depends(get_db), _: None = Depends(require_office)):
    ws = _week_start() if not week_start else date.fromisoformat(week_start)
    # Get assignments
    if not _has(db, "promoter_store_assignments"):
        return Response(content="username,store_id,status\n", media_type="text/csv")
    ass = db.execute(text("select promoter_username, store_id from promoter_store_assignments")).mappings().all()
    # Get who reported
    reported = set()
    if _has(db, "promoter_stock_reports"):
        rows = db.execute(text("select distinct promoter_username, store_id from promoter_stock_reports where week_start=:ws"), {"ws": ws}).mappings().all()
        reported = set((r["promoter_username"], r["store_id"]) for r in rows)
    # Build CSV
    lines = ["username,store_id,status"]
    for a in ass:
        key = (a["promoter_username"], a["store_id"])
        status = "OK" if key in reported else "MISSING"
        lines.append(f"{a['promoter_username']},{a['store_id']},{status}")
    csv = "\n".join(lines) + "\n"
    return Response(content=csv, media_type="text/csv")
