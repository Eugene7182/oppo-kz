from __future__ import annotations
from datetime import date
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _df(db: Session, sql: str, params: dict | None = None) -> pd.DataFrame:
    return pd.DataFrame(db.execute(text(sql), params or {}).mappings())

def set_plan(db: Session, store_id: str, month: str, plan_qty: int, created_by: str | None):
    if not _has(db, "plans_store_month"): raise RuntimeError("plans_store_month missing")
    _df(db, "insert into plans_store_month (store_id, month, plan_qty, created_by) values (:s, :m, :q, :u) "
            "on conflict (store_id, month) do update set plan_qty=excluded.plan_qty, updated_at=now()",
        {"s": store_id, "m": month, "q": int(plan_qty), "u": created_by})
    return {"store_id": store_id, "month": month, "plan_qty": int(plan_qty)}

def get_plans_for_city(db: Session, city: str, month: str):
    if not (_has(db, "plans_store_month") and _has(db, "stores")): return {"rows": []}
    sql = """
      select p.store_id, s.store_name, s.city_code, p.month, p.plan_qty
      from plans_store_month p join stores s on s.store_id = p.store_id
      where s.city_code = :city and p.month = :m
      order by s.store_name
    """
    df = _df(db, sql, {"city": city, "m": month})
    return {"rows": ([] if df.empty else df.to_dict("records"))}

def get_plans_all(db: Session, month: str):
    if not (_has(db, "plans_store_month") and _has(db, "stores")): return {"rows": []}
    sql = """
      select p.store_id, s.store_name, s.city_code, p.month, p.plan_qty
      from plans_store_month p join stores s on s.store_id = p.store_id
      where p.month = :m
      order by s.city_code, s.store_name
    """
    df = _df(db, sql, {"m": month})
    return {"rows": ([] if df.empty else df.to_dict("records"))}
