from __future__ import annotations
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _df(db: Session, sql: str, params: dict | None = None) -> pd.DataFrame:
    return pd.DataFrame(db.execute(text(sql), params or {}).mappings())

def classify_abcxyz(db: Session, days: int = 60):
    if not _has(db, "sales_daily"):
        return {"items": []}
    df = _df(db, "select date, store_id, sku_id, model, qty from sales_daily where date >= current_date - interval :span", {"span": f"{days} day"})
    if df.empty: return {"items": []}
    # ABC by total qty per SKU
    by_sku = df.groupby("sku_id")["qty"].sum().sort_values(ascending=False)
    total = by_sku.sum() or 1.0
    share = (by_sku / total).cumsum()
    abc = {}
    for sku, cum in share.items():
        if cum <= 0.8: abc[sku] = "A"
        elif cum <= 0.95: abc[sku] = "B"
        else: abc[sku] = "C"
    # XYZ by CV (std/mean) per SKU per day
    daily = df.groupby(["sku_id","date"])["qty"].sum().reset_index()
    stats = daily.groupby("sku_id")["qty"].agg(["mean","std"]).fillna(0.0)
    stats["cv"] = stats.apply(lambda r: (r["std"] / (r["mean"] + 1e-6)), axis=1)
    xyz = {}
    for sku, cv in stats["cv"].to_dict().items():
        if cv <= 0.1: xyz[sku] = "X"
        elif cv <= 0.25: xyz[sku] = "Y"
        else: xyz[sku] = "Z"
    # Merge
    out = []
    for sku, qty in by_sku.items():
        out.append({"sku_id": str(sku), "total_qty": float(qty), "ABC": abc.get(sku, "C"), "XYZ": xyz.get(sku, "Z")})
    return {"items": out}
