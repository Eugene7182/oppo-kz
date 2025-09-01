from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from datetime import date
from app.bonus.service import estimate_bonus

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _df(db: Session, sql: str, params: dict | None = None) -> pd.DataFrame:
    return pd.DataFrame(db.execute(text(sql), params or {}).mappings())

def _month_start() -> str:
    return pd.to_datetime(date.today().replace(day=1)).date().isoformat()

def promoter_month_progress(db: Session, promoter_username: str):
    ms = _month_start()
    qty_mtd = 0.0
    if _has(db, "sales_daily") and "promoter" in [c['column_name'] for c in db.execute(text("select column_name from information_schema.columns where table_name='sales_daily'")).mappings()]:
        row = db.execute(text("select sum(qty) qty from sales_daily where promoter=:p and date >= :ms"), {"p": promoter_username, "ms": ms}).mappings().first()
        qty_mtd = float(row["qty"] or 0) if row else 0.0
    elif _has(db, "promoter_store_assignments"):
        stores = _df(db, "select store_id from promoter_store_assignments where promoter_username=:p", {"p": promoter_username})
        if not stores.empty and _has(db, "sales_daily"):
            ids = stores["store_id"].tolist()
            row = db.execute(text("select sum(qty) qty from sales_daily where store_id = any(:s) and date >= :ms"), {"s": ids, "ms": ms}).mappings().first()
            qty_mtd = float(row["qty"] or 0) if row else 0.0
    plan_qty = 0.0
    if _has(db, "plans_store_month") and _has(db, "promoter_store_assignments"):
        stores = _df(db, "select store_id from promoter_store_assignments where promoter_username=:p", {"p": promoter_username})
        if not stores.empty:
            ids = stores["store_id"].tolist()
            row = db.execute(text("select sum(plan_qty) plan from plans_store_month where month = :ms and store_id = any(:s)"), {"ms": ms, "s": ids}).mappings().first()
            plan_qty = float(row["plan"] or 0) if row else 0.0
    progress = (qty_mtd / plan_qty * 100.0) if plan_qty > 0 else 0.0
    days_passed = _df(db, "select extract(day from (current_date - date_trunc('month', current_date))) as days").iloc[0].get('days', 1) or 1
    runrate_qty = qty_mtd / max(1.0, float(days_passed))
    eom_qty = runrate_qty * 30.0
    bonus = estimate_bonus(db, promoter_username=promoter_username)
    return {"month": ms, "mtd_qty": qty_mtd, "plan_qty": plan_qty, "progress_pct": progress, "runrate_qty": runrate_qty, "eom_qty": eom_qty, "bonus": bonus}
