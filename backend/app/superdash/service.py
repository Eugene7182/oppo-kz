
from __future__ import annotations
from datetime import date, datetime, timedelta
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _df(db: Session, sql: str, params: dict | None = None) -> pd.DataFrame:
    return pd.DataFrame(db.execute(text(sql), params or {}).mappings())

TBL_STORES = 'stores'
TBL_SALES = 'sales_daily'

class SuperError(RuntimeError):
    pass

def _stores_for_super(db: Session, supervisor: str | None):
    if not _has(db, TBL_STORES):
        return pd.DataFrame()
    if supervisor:
        return _df(db, f"select store_id, city_code, store_name, network_id from {TBL_STORES} where supervisor_name=:s", {"s": supervisor})
    return _df(db, f"select store_id, city_code, store_name, network_id from {TBL_STORES}", {})

def stocks_current(db: Session, supervisor: str | None = None, limit: int = 500):
    stores = _stores_for_super(db, supervisor)
    if stores.empty:
        return {"items": []}
    sql = """
      with last as (
        select distinct on (r.store_id, r.sku_id)
               r.store_id, r.sku_id, r.on_hand, r.reported_at
        from promoter_stock_reports r
        order by r.store_id, r.sku_id, r.reported_at desc
      )
      select s.store_id, s.store_name, s.city_code, s.network_id, l.sku_id, l.on_hand, l.reported_at
      from last l join stores s on s.store_id = l.store_id
      where s.store_id = any(:stores) 
      order by l.reported_at desc
      limit :limit
    """
    df = _df(db, sql, {"stores": stores["store_id"].tolist(), "limit": int(limit)})
    return {"items": ([] if df.empty else df.to_dict("records"))}

def promoter_sales(db: Session, supervisor: str | None = None, date_from: str | None = None, date_to: str | None = None, group_by: str = 'model'):
    if not _has(db, TBL_SALES):
        return {"rows": []}
    cond = "where 1=1"
    params: dict = {}
    if date_from:
        cond += " and date >= :dfrom"; params["dfrom"] = date_from
    if date_to:
        cond += " and date <= :dto"; params["dto"] = date_to
    if supervisor and _has(db, TBL_STORES):
        store_ids = _df(db, "select store_id from stores where supervisor_name=:s", {"s": supervisor})
        if not store_ids.empty:
            cond += " and store_id = any(:stores)"; params["stores"] = store_ids["store_id"].tolist()
    key = "model" if group_by not in ("sku","promoter") else group_by
    sql = f"select {key} as key, sum(qty) as qty from sales_daily {cond} group by {key} order by qty desc limit 50"
    df = _df(db, sql, params)
    return {"rows": ([] if df.empty else df.to_dict("records"))}

def city_heatmap(db: Session, supervisor: str | None = None, days: int = 7) -> dict:
    if not _has(db, TBL_STORES):
        return {"items": []}
    stores = _stores_for_super(db, supervisor)
    store_ids = stores["store_id"].tolist() if not stores.empty else []
    extra = " and s.store_id = any(:stores)" if store_ids else ""
    sales_sql = f"""
      select st.city_code, sum(s.qty) as qty, sum(s.revenue) as revenue
      from sales_daily s
      join stores st on st.store_id = s.store_id
      where s.date >= current_date - interval :span{extra}
      group by st.city_code
    """
    params_sales: dict = {"span": f"{days} day"}
    if store_ids:
        params_sales["stores"] = store_ids
    sales = _df(db, sales_sql, params_sales)
    stock_sql = """
      with last as (
        select distinct on (r.store_id, r.sku_id)
               r.store_id, r.sku_id, r.on_hand
        from promoter_stock_reports r
        order by r.store_id, r.sku_id, r.reported_at desc
      )
      select st.city_code, sum(coalesce(l.on_hand,0)) as on_hand
      from last l join stores st on st.store_id = l.store_id
    """
    if store_ids:
        stock_sql += " where st.store_id = any(:stores)"
    stock_sql += " group by st.city_code"
    params_stock: dict = {"stores": store_ids} if store_ids else {}
    stock = _df(db, stock_sql, params_stock)

    res: dict = {}
    if not sales.empty:
        for _, r in sales.iterrows():
            key = str(r["city_code"])
            res.setdefault(key, {"city_code": key, "qty": 0.0, "revenue": 0.0, "on_hand": 0.0})
            res[key]["qty"] += float(r["qty"] or 0.0)
            res[key]["revenue"] += float(r["revenue"] or 0.0)
    if not stock.empty:
        for _, r in stock.iterrows():
            key = str(r["city_code"])
            res.setdefault(key, {"city_code": key, "qty": 0.0, "revenue": 0.0, "on_hand": 0.0})
            res[key]["on_hand"] += float(r["on_hand"] or 0.0)
    return {"items": list(res.values())}


def summary(db: Session, supervisor: str | None = None, scope: str = 'week', city: str | None = None):
    if not _has(db, TBL_SALES):
        return {"period": {}, "total": {"qty": 0, "revenue": 0}}
    cond = "where 1=1"
    params = {}
    if scope == 'today':
        cond += " and date = current_date"
    elif scope == 'yesterday':
        cond += " and date = current_date - interval '1 day'"
    elif scope == 'month':
        cond += " and date >= date_trunc('month', current_date)"
    else:
        cond += " and date >= current_date - interval '7 day'"
    if supervisor and _has(db, TBL_STORES):
        store_ids = _df(db, "select store_id, city_code from stores where supervisor_name=:s", {"s": supervisor})
        if not store_ids.empty:
            if city:
                store_ids = store_ids[store_ids["city_code"]==city]
            ids = store_ids["store_id"].tolist()
            if ids:
                cond += " and store_id = any(:stores)"; params["stores"] = ids
    df = _df(db, f"select sum(qty) qty, sum(revenue) revenue from {TBL_SALES} {cond}", params)
    return {"period": {"scope": scope}, "total": ({"qty": 0, "revenue": 0} if df.empty else df.iloc[0].to_dict())}

def weekly_vs(db: Session, supervisor: str | None = None, city: str | None = None, weeks: int = 8):
    if not _has(db, TBL_SALES):
        return {"weeks": []}
    cond = "where 1=1"
    params = {}
    if supervisor and _has(db, TBL_STORES):
        store_ids = _df(db, "select store_id, city_code from stores where supervisor_name=:s", {"s": supervisor})
        if not store_ids.empty:
            if city:
                store_ids = store_ids[store_ids["city_code"]==city]
            ids = store_ids["store_id"].tolist()
            if ids:
                cond += " and store_id = any(:stores)"; params["stores"] = ids
    df = _df(db, f"select to_char(date_trunc('week', date), 'IYYY-IW') as week, sum(qty) qty from {TBL_SALES} {cond} group by 1 order by 1 desc limit :n", {**params, "n": int(weeks)})
    return {"weeks": ([] if df.empty else list(reversed(df.to_dict('records'))))}
