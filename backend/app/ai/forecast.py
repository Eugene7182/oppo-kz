from __future__ import annotations
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _df(db: Session, sql: str, params: dict | None = None) -> pd.DataFrame:
    return pd.DataFrame(db.execute(text(sql), params or {}).mappings())

def forecast_sales(db: Session, group_by: str = "total", horizon_days: int = 30):
    if not _has(db, "sales_daily"):
        return {"series": [], "forecast": []}
    if group_by == "model":
        sql = "select date, model as key, sum(qty) as qty from sales_daily group by 1,2 order by 1"
    elif group_by == "sku":
        sql = "select date, sku_id as key, sum(qty) as qty from sales_daily group by 1,2 order by 1"
    else:
        sql = "select date, 'total' as key, sum(qty) as qty from sales_daily group by 1 order by 1"
    df = _df(db, sql, {})
    if df.empty:
        return {"series": [], "forecast": []}
    df["date"] = pd.to_datetime(df["date"])
    out_series = []
    out_fore = []
    for key, g in df.groupby("key"):
        g = g.sort_values("date").set_index("date")
        # simple EWMA as baseline
        g["ewm"] = g["qty"].ewm(span=7, adjust=False).mean()
        last_date = g.index.max()
        last_val = float(g["ewm"].iloc[-1]) if not g.empty else 0.0
        # naive flat forecast
        f = []
        for i in range(1, horizon_days+1):
            f.append({"date": (last_date + pd.Timedelta(days=i)).date().isoformat(), "key": str(key), "qty": last_val})
        out_series.extend([{"date": d.date().isoformat(), "key": str(key), "qty": float(v)} for d, v in g["qty"].items()])
        out_fore.extend(f)
    return {"series": out_series, "forecast": out_fore}
