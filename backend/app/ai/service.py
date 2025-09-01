from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
import math
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _df(db: Session, sql: str, params: dict | None = None) -> pd.DataFrame:
    return pd.DataFrame(db.execute(text(sql), params or {}).mappings())

@dataclass
class RecoParams:
    days: int = 28           # horizon to compute avg demand
    leadtime: int = 3        # days to deliver
    target_days: int = 7     # target shelf days
    min_qty: int = 1         # filter small recos
    same_city_only: bool = True
    same_network_only: bool = True

def _avg_daily_demand(db: Session, days: int) -> pd.DataFrame:
    if not _has(db, "sales_daily"):
        return pd.DataFrame(columns=["store_id","sku_id","avg_daily","sum_qty"])
    sql = "select store_id, sku_id, sum(qty) as sum_qty from sales_daily where date >= current_date - interval :span group by 1,2"
    df = _df(db, sql, {"span": f"{days} day"})
    if df.empty:
        df["avg_daily"] = []
        return df
    df["avg_daily"] = df["sum_qty"].astype(float) / float(days)
    return df

def _latest_stock(db: Session) -> pd.DataFrame:
    if not _has(db, "promoter_stock_reports"):
        return pd.DataFrame(columns=["store_id","sku_id","on_hand"])
    sql = '''
      select distinct on (store_id, sku_id) store_id, sku_id, on_hand
      from promoter_stock_reports
      order by store_id, sku_id, reported_at desc
    '''
    return _df(db, sql, {})

def _store_meta(db: Session) -> pd.DataFrame:
    if not _has(db, "stores"):
        return pd.DataFrame(columns=["store_id","city_code","network_id"])
    return _df(db, "select store_id, city_code, network_id from stores", {})

def recommend_replenish(db: Session, params: RecoParams) -> dict:
    demand = _avg_daily_demand(db, params.days)
    stock = _latest_stock(db)
    stores = _store_meta(db)

    if demand.empty and stock.empty:
        return {"items": []}

    base = pd.merge(demand, stock, on=["store_id","sku_id"], how="outer")
    base["avg_daily"] = base["avg_daily"].fillna(0.0)
    base["on_hand"] = base["on_hand"].fillna(0).astype(float)
    base = pd.merge(base, stores, on="store_id", how="left")

    target_level = (params.leadtime + params.target_days)  # days of cover we want
    base["target_units"] = base["avg_daily"] * float(target_level)
    base["rec_qty"] = (base["target_units"] - base["on_hand"]).apply(lambda x: max(0, math.ceil(x)))
    base = base[base["rec_qty"] >= params.min_qty]

    items = base.sort_values(["city_code","network_id","store_id","sku_id"]).to_dict("records")
    return {"items": items}

def recommend_transfer(db: Session, params: RecoParams) -> dict:
    # compute recommended target and surplus/deficit per store/sku
    r = recommend_replenish(db, params)["items"]
    if not r:
        return {"pairs": []}
    df = pd.DataFrame(r)
    # compute upper threshold for surplus
    df["upper"] = (df["avg_daily"] * float(params.leadtime + params.target_days) * 1.2).astype(float)
    df["surplus"] = (df["on_hand"] - df["upper"]).apply(lambda x: max(0.0, x))
    df["deficit"] = df["rec_qty"].astype(float)
    # candidate sources and targets
    src = df[df["surplus"] > 0.5].copy()
    dst = df[df["deficit"] > 0.5].copy()

    pairs = []
    # match within same city/network
    for _, d in dst.iterrows():
        # filter sources for same sku and city/network
        sfil = src[src["sku_id"] == d["sku_id"]]
        if params.same_city_only:
            sfil = sfil[sfil["city_code"] == d.get("city_code")]
        if params.same_network_only:
            sfil = sfil[sfil["network_id"] == d.get("network_id")]
        if sfil.empty:
            continue
        needed = float(d["deficit"])
        for _, s in sfil.sort_values("surplus", ascending=False).iterrows():
            if needed <= 0:
                break
            take = min(float(s["surplus"]), needed)
            if take < 1:
                continue
            pairs.append({
                "sku_id": str(d["sku_id"]),
                "from_store": str(s["store_id"]),
                "to_store": str(d["store_id"]),
                "qty": int(math.floor(take)),
                "city_code": d.get("city_code"),
                "network_id": d.get("network_id"),
            })
            # update running surplus/need
            src.loc[(src["store_id"]==s["store_id"]) & (src["sku_id"]==s["sku_id"]), "surplus"] = float(s["surplus"]) - take
            needed -= take
    return {"pairs": pairs}

def detect_anomalies(db: Session, weeks_back: int = 2) -> dict:
    # compare last 7d vs prev 7d per store/sku
    if not _has(db, "sales_daily"):
        return {"items": []}
    sql = "select date, store_id, sku_id, qty from sales_daily where date >= current_date - interval '14 day'"
    df = _df(db, sql, {})
    if df.empty:
        return {"items": []}
    df["date"] = pd.to_datetime(df["date"]).dt.date
    last7 = date.today() - timedelta(days=6)
    prev7_start = last7 - timedelta(days=7)
    a = df[(df["date"] >= last7)]
    b = df[(df["date"] >= prev7_start) & (df["date"] < last7)]
    A = a.groupby(["store_id","sku_id"])["qty"].sum().rename("qty_7")
    B = b.groupby(["store_id","sku_id"])["qty"].sum().rename("qty_prev7")
    merged = pd.concat([A, B], axis=1).fillna(0.0).reset_index()
    def label(row):
        q1, q0 = float(row["qty_7"]), float(row["qty_prev7"])
        if q0 < 5 and q1 < 5:
            return None
        change = (q1 - q0) / (q0 + 1e-6)
        if change >= 1.5:
            return ("surge", change)
        if change <= -0.5:
            return ("drop", change)
        return None
    out = []
    for _, r in merged.iterrows():
        lab = label(r)
        if lab:
            kind, delta = lab
            out.append({"store_id": str(r["store_id"]), "sku_id": str(r["sku_id"]), "qty_7": float(r["qty_7"]), "qty_prev7": float(r["qty_prev7"]), "kind": kind, "change": float(delta)})
    return {"items": out}
