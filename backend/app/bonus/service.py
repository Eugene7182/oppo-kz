from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from typing import Dict

def _has(db: Session, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _row(db: Session, sql: str, params: dict):
    r = db.execute(text(sql), params).mappings().first()
    return dict(r) if r else {}

def get_bonus_for_network(db: Session, network_id: str) -> dict:
    if not _has(db, "network_bonus"): return {"base_bonus": 0.0}
    r = _row(db, "select base_bonus, t1_qty, t1_bonus, t2_qty, t2_bonus, t3_qty, t3_bonus from network_bonus where network_id=:n", {"n": network_id})
    return r or {"base_bonus": 0.0}

def _bonus_hist_amount(db: Session, network_id: str, sku_id: str, on_date: date) -> float | None:
    if not _has(db, "network_phone_bonus_hist"):
        return None
    r = _row(db, """
        select amount from network_phone_bonus_hist
        where network_id=:n and sku_id=:s and valid_from <= :d
          and (valid_to is null or valid_to >= :d)
        order by valid_from desc
        limit 1
    """, {"n": network_id, "s": sku_id, "d": on_date})
    if r: return float(r.get("amount") or 0.0)
    return None

def estimate_bonus(db: Session, *, promoter_username: str) -> dict:
    # Month scope
    on_date = date.today().replace(day=1)
    total_bonus = 0.0
    details = []

    has_sales = _has(db, "sales_daily")
    has_assign = _has(db, "promoter_store_assignments")

    has_promoter_col = False
    cols = []
    if has_sales:
        cols = [c['column_name'] for c in db.execute(text("select column_name from information_schema.columns where table_name='sales_daily'")).mappings()]
        has_promoter_col = "promoter" in cols or "promoter_username" in cols

    rows = []
    if has_sales and has_promoter_col:
        prom_col = "promoter" if "promoter" in cols else "promoter_username"
        rows = db.execute(text(f"""
            select store_id, network_id, sku_id, sum(qty) qty
            from sales_daily
            where {prom_col}=:p and date >= date_trunc('month', current_date)
            group by store_id, network_id, sku_id
        """), {"p": promoter_username}).mappings().all()
    elif has_assign:
        rows = db.execute(text("""
            select a.store_id, s.network_id, null as sku_id, 0 as qty
            from promoter_store_assignments a
            join stores s on s.store_id = a.store_id
            where a.promoter_username=:p
        """), {"p": promoter_username}).mappings().all()

    for r in rows:
        network = r.get("network_id")
        qty = float(r.get("qty", 0) or 0)
        sku_id = r.get("sku_id")
        per = 0.0
        if network:
            # Prefer versioned per-sku amount for current month
            if sku_id:
                hist_amt = _bonus_hist_amount(db, network, str(sku_id), on_date)
                if hist_amt is not None:
                    per = hist_amt
                elif _has(db, "network_phone_bonus"):
                    # fallback to non-versioned grid if exists
                    g = _row(db, "select amount from network_phone_bonus where network_id=:n and sku_id=:s", {"n": network, "s": sku_id})
                    if g: per = float(g.get("amount") or 0.0)
            if per == 0.0:
                # legacy network tier fallback
                nb = get_bonus_for_network(db, network)
                base = float(nb.get("base_bonus") or 0.0)
                t1q, t1b = (nb.get("t1_qty"), nb.get("t1_bonus"))
                t2q, t2b = (nb.get("t2_qty"), nb.get("t2_bonus"))
                t3q, t3b = (nb.get("t3_qty"), nb.get("t3_bonus"))
                per = base
                if t3q and qty >= t3q and t3b is not None: per = float(t3b)
                elif t2q and qty >= t2q and t2b is not None: per = float(t2b)
                elif t1q and qty >= t1q and t1b is not None: per = float(t1b)

        bonus = per * qty
        total_bonus += bonus
        details.append({"store_id": r.get("store_id"), "network_id": network, "sku_id": sku_id, "qty": qty, "per_unit": per, "bonus": bonus})
    return {"total_bonus": total_bonus, "details": details}
