from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from datetime import date

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _df(db: Session, sql: str, params: dict | None = None) -> pd.DataFrame:
    return pd.DataFrame(db.execute(text(sql), params or {}).mappings())

def month_start() -> str:
    today = date.today()
    return date(today.year, today.month, 1).isoformat()

def kpi_city(db: Session, city: str, month: str | None = None):
    m = month or month_start()
    if not (_has(db, "sales_daily") and _has(db, "plans_store_month") and _has(db, "stores")):
        return {"city": city, "month": m, "plan": 0, "fact": 0, "progress": 0, "stores": []}
    sql = """
      select s.store_id, s.store_name,
             coalesce(p.plan_qty,0) as plan_qty,
             coalesce(f.fact_qty,0) as fact_qty
      from stores s
      left join plans_store_month p on p.store_id = s.store_id and p.month=:m
      left join (
        select store_id, sum(qty) as fact_qty
        from sales_daily
        where date >= :m
        group by store_id
      ) f on f.store_id = s.store_id
      where s.city_code = :city
      order by s.store_name
    """
    df = _df(db, sql, {"city": city, "m": m})
    total_plan = int(df["plan_qty"].sum()) if not df.empty else 0
    total_fact = int(df["fact_qty"].sum()) if not df.empty else 0
    progress = (total_fact / total_plan * 100.0) if total_plan > 0 else 0.0
    rows = ([] if df.empty else df.assign(progress=lambda d: (d["fact_qty"]/d["plan_qty"]*100.0).fillna(0.0)).to_dict("records"))
    return {"city": city, "month": m, "plan": total_plan, "fact": total_fact, "progress": progress, "stores": rows}

def kpi_office(db: Session, month: str | None = None):
    m = month or month_start()
    if not (_has(db, "sales_daily") and _has(db, "plans_store_month") and _has(db, "stores")):
        return {"month": m, "plan": 0, "fact": 0, "progress": 0, "cities": []}
    sql = """
      with city as (
        select s.city_code,
               sum(coalesce(p.plan_qty,0)) as plan_qty,
               sum(coalesce(f.fact_qty,0)) as fact_qty
        from stores s
        left join plans_store_month p on p.store_id = s.store_id and p.month=:m
        left join (
          select store_id, sum(qty) as fact_qty
          from sales_daily
          where date >= :m
          group by store_id
        ) f on f.store_id = s.store_id
        group by s.city_code
      )
      select * from city order by city_code
    """
    df = _df(db, sql, {"m": m})
    total_plan = int(df["plan_qty"].sum()) if not df.empty else 0
    total_fact = int(df["fact_qty"].sum()) if not df.empty else 0
    progress = (total_fact / total_plan * 100.0) if total_plan > 0 else 0.0
    rows = ([] if df.empty else df.assign(progress=lambda d: (d["fact_qty"]/d["plan_qty"]*100.0).fillna(0.0)).to_dict("records"))
    return {"month": m, "plan": total_plan, "fact": total_fact, "progress": progress, "cities": rows}
