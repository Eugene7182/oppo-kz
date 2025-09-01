from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import csv, io, json
from datetime import date, timedelta
from app.api.v1.deps import get_db, get_current_user, require_office_or_supervisor_or_admin as require_power

router = APIRouter(prefix="/bonus", tags=["bonus"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.post("/grid/import")
async def import_bonus_csv(file: UploadFile = File(...), network_id: str = Form(...), month: str = Form(None),
                           db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_power)):
    if not _has(db, "network_phone_bonus_hist"):
        raise HTTPException(status_code=503, detail="bonus history table missing")
    if not month:
        month = date.today().replace(day=1).isoformat()
    content = await file.read()
    try:
        txt = content.decode('utf-8-sig')
    except Exception:
        txt = content.decode('utf-8', errors='ignore')
    reader = csv.DictReader(io.StringIO(txt))
    required = {"sku_id", "amount"}
    if not required.issubset(set([c.strip().lower() for c in (reader.fieldnames or [])])):
        raise HTTPException(status_code=400, detail="CSV must have columns: sku_id, amount")
    prev_end = (date.fromisoformat(month) - timedelta(days=1)).isoformat()
    db.execute(text("""
        update network_phone_bonus_hist set valid_to=:prev_end
        where network_id=:n and valid_to is null and valid_from < :m
    """), {"n": network_id, "m": month, "prev_end": prev_end})
    cnt=0
    for row in reader:
        sku = str(row.get("sku_id") or row.get("SKU_ID") or "").strip()
        amt = float(row.get("amount") or row.get("AMOUNT") or 0)
        if not sku: 
            continue
        db.execute(text("""
            insert into network_phone_bonus_hist(network_id, sku_id, amount, valid_from)
            values (:n,:s,:a,:m)
        """), {"n": network_id, "s": sku, "a": amt, "m": month})
        cnt += 1
    db.commit()
    if _has(db, "audit_log"):
        db.execute(text("insert into audit_log(event_type, actor, meta) values ('bonus_grid_import_csv', :a, cast(:m as jsonb))"),
                   {"a": getattr(user,'username',None), "m": json.dumps({"network_id": network_id, "month": month, "rows": cnt})})
        db.commit()
    return {"ok": True, "imported": cnt, "network_id": network_id, "month": month}

@router.get("/grid/export")
def export_bonus_csv(network_id: str = Query(...), month: str | None = Query(None),
                     db: Session = Depends(get_db), _: None = Depends(require_power)):
    if not _has(db, "skus"): 
        raise HTTPException(status_code=503, detail="skus missing")
    if month and _has(db, "network_phone_bonus_hist"):
        rows = db.execute(text("""
            with sel as (
              select sku_id, amount
              from network_phone_bonus_hist
              where network_id=:n and valid_from <= :m and (valid_to is null or valid_to >= :m)
              order by valid_from desc
            )
            select s.sku_id, s.display_name as model, coalesce((select amount from sel where sel.sku_id=s.sku_id),0) as amount
            from skus s
            order by s.display_name
        """), {"n": network_id, "m": month}).mappings().all()
    else:
        if not _has(db, "network_phone_bonus"):
            raise HTTPException(status_code=503, detail="no bonus grid available to export")
        rows = db.execute(text("""
            select s.sku_id, s.display_name as model, coalesce(b.amount,0) as amount
            from skus s left join network_phone_bonus b on b.sku_id = s.sku_id and b.network_id = :n
            order by s.display_name
        """), {"n": network_id}).mappings().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["sku_id","model","amount"])
    for r in rows:
        writer.writerow([r["sku_id"], r["model"], r["amount"]])
    data = output.getvalue()
    return Response(content=data, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=bonus_{network_id}.csv"})
