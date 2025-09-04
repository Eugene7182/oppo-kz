
from __future__ import annotations
from datetime import date, timedelta
from collections import defaultdict
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.sales import SalesNetwork
from app.models.inventory import StockBalance

def _demand_last_days(db: Session, days: int = 30):
    since = date.today() - timedelta(days=days)
    q = db.query(SalesNetwork.store_id, SalesNetwork.sku_id, func.sum(SalesNetwork.qty))\
          .filter(SalesNetwork.sold_at >= since)\
          .group_by(SalesNetwork.store_id, SalesNetwork.sku_id)
    res = defaultdict(int)
    for store_id, sku_id, qty in q.all():
        res[(store_id, sku_id)] = int(qty or 0)
    return res

def _balances(db: Session):
    res = defaultdict(lambda: {"on_hand":0.0, "in_transit":0.0})
    for b in db.query(StockBalance).all():
        res[(b.store_id, b.sku_id)] = {"on_hand": float(b.on_hand), "in_transit": float(b.in_transit)}
    return res

def recommend_moves(db: Session, *, max_moves: int = 20, horizon_days: int = 30, safety_days: int = 7):
    dem = _demand_last_days(db, days=horizon_days)
    bal = _balances(db)
    if not dem and not bal:
        return {"moves": [], "explain": "Нет данных продаж/остатков"}
    avg_daily = defaultdict(float)
    for (store_id, sku_id), qty in dem.items():
        avg_daily[(store_id, sku_id)] = qty / float(max(horizon_days, 1))
    surplus_by_store_sku = {}
    deficit_by_store_sku = {}
    sku_set = set([k[1] for k in dem.keys()] + [k[1] for k in bal.keys()])
    for sku_id in sku_set:
        store_ids = set([s for (s,sk) in dem.keys() if sk == sku_id] + [s for (s,sk) in bal.keys() if sk == sku_id])
        for store_id in store_ids:
            b = bal.get((store_id, sku_id), {"on_hand":0.0,"in_transit":0.0})
            on_hand = b["on_hand"]
            need = avg_daily.get((store_id, sku_id), 0.0) * safety_days
            diff = on_hand - need
            if diff > 0.5: surplus_by_store_sku[(store_id, sku_id)] = diff
            elif diff < -0.5: deficit_by_store_sku[(store_id, sku_id)] = -diff
    donors = sorted(surplus_by_store_sku.items(), key=lambda x: x[1], reverse=True)
    receivers = sorted(deficit_by_store_sku.items(), key=lambda x: x[1], reverse=True)
    moves: List[Dict[str, Any]] = []; i = j = 0
    while i < len(donors) and j < len(receivers) and len(moves) < max_moves:
        (d_store, sku), d_qty = donors[i]
        (r_store, r_sku), r_qty = receivers[j]
        if sku != r_sku:
            if sku < r_sku: i += 1
            else: j += 1
            continue
        qty = float(min(d_qty, r_qty))
        if qty >= 1:
            moves.append({
                "sku_id": sku, "from_store_id": d_store, "to_store_id": r_store, "qty": int(qty),
                "why": f"Профицит≈{d_qty:.1f} у {d_store} → дефицит≈{r_qty:.1f} у {r_store} (safety={safety_days}д)"
            })
            donors[i] = ((d_store, sku), d_qty - qty)
            receivers[j] = ((r_store, sku), r_qty - qty)
            if donors[i][1] < 1: i += 1
            if receivers[j][1] < 1: j += 1
        else:
            i += 1; j += 1
    explain = f"Учитываем остатки on_hand и спрос за {horizon_days}д; safety stock = avg_daily * {safety_days}"
    return {"moves": moves, "explain": explain}
