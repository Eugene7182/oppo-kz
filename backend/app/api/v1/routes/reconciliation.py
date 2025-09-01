# backend/app/api/v1/routes/reconciliation.py
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ....models import Store, SKU, PromoterSale, SalesNetwork, SalesFinal
from ..deps import get_db, require_super

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])


def _apply_common_filters_to_promoter(q, date_from: date | None, date_to: date | None,
                                      store_id: int | None, network: str | None):
    if date_from:
        q = q.filter(PromoterSale.sold_at >= date_from)
    if date_to:
        q = q.filter(PromoterSale.sold_at <= date_to)
    if store_id:
        q = q.filter(PromoterSale.store_id == store_id)
    if network:
        q = q.join(Store, Store.id == PromoterSale.store_id).filter(Store.network == network)
    return q


def _apply_common_filters_to_network(q, date_from: date | None, date_to: date | None,
                                     store_id: int | None, network: str | None):
    if date_from:
        q = q.filter(SalesNetwork.sold_at >= date_from)
    if date_to:
        q = q.filter(SalesNetwork.sold_at <= date_to)
    if store_id:
        q = q.filter(SalesNetwork.store_id == store_id)
    if network:
        q = q.join(Store, Store.id == SalesNetwork.store_id).filter(Store.network == network)
    return q


@router.get("")
def reconciliation_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    store_id: int | None = Query(default=None),
    network: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _super=Depends(require_super),
) -> list[dict[str, Any]]:
    """
    Сводная таблица: продажи промоутеров vs продажи сети по ключу (store_id, sku_id, date).
    """
    # агрегат по промоутерам
    q_promoter = (
        db.query(
            PromoterSale.store_id.label("store_id"),
            PromoterSale.sku_id.label("sku_id"),
            PromoterSale.sold_at.label("date"),
            func.sum(PromoterSale.qty).label("qty"),
            func.sum(func.coalesce(PromoterSale.amount, 0)).label("amount"),
        )
        .group_by(PromoterSale.store_id, PromoterSale.sku_id, PromoterSale.sold_at)
    )
    q_promoter = _apply_common_filters_to_promoter(q_promoter, date_from, date_to, store_id, network)
    promoter_rows = q_promoter.all()

    # агрегат по сети
    q_network = (
        db.query(
            SalesNetwork.store_id.label("store_id"),
            SalesNetwork.sku_id.label("sku_id"),
            SalesNetwork.sold_at.label("date"),
            func.sum(SalesNetwork.qty).label("qty"),
            func.sum(SalesNetwork.amount).label("amount"),
        )
        .group_by(SalesNetwork.store_id, SalesNetwork.sku_id, SalesNetwork.sold_at)
    )
    q_network = _apply_common_filters_to_network(q_network, date_from, date_to, store_id, network)
    network_rows = q_network.all()

    # слить по ключу
    def key(r) -> Tuple[int, int, date]:
        return (int(r.store_id), int(r.sku_id), r.date)

    merged: Dict[Tuple[int, int, date], Dict[str, Any]] = {}

    for r in promoter_rows:
        merged[key(r)] = {
            "store_id": int(r.store_id),
            "sku_id": int(r.sku_id),
            "date": r.date.isoformat(),
            "promoter_qty": int(r.qty or 0),
            "promoter_amount": float(r.amount or 0),
            "network_qty": 0,
            "network_amount": 0.0,
        }

    for r in network_rows:
        k = key(r)
        row = merged.get(k)
        if not row:
            row = {
                "store_id": int(r.store_id),
                "sku_id": int(r.sku_id),
                "date": r.date.isoformat(),
                "promoter_qty": 0,
                "promoter_amount": 0.0,
                "network_qty": 0,
                "network_amount": 0.0,
            }
            merged[k] = row
        row["network_qty"] = int(r.qty or 0)
        row["network_amount"] = float(r.amount or 0)

    # расчёт разниц + обогащение справочниками (опционально)
    store_ids = {m["store_id"] for m in merged.values()}
    sku_ids = {m["sku_id"] for m in merged.values()}

    stores = {s.id: s for s in db.query(Store).filter(Store.id.in_(store_ids)).all()} if store_ids else {}
    skus = {s.id: s for s in db.query(SKU).filter(SKU.id.in_(sku_ids)).all()} if sku_ids else {}

    result: list[dict[str, Any]] = []
    for m in merged.values():
        m["diff_qty"] = int(m["promoter_qty"]) - int(m["network_qty"])
        m["diff_amount"] = float(m["promoter_amount"]) - float(m["network_amount"])

        st = stores.get(m["store_id"])
        if st:
            m["store_name"] = st.name
            m["store_city"] = st.city
            m["store_network"] = st.network

        sku = skus.get(m["sku_id"])
        if sku:
            m["sku_brand"] = sku.brand
            m["sku_model"] = sku.model
            m["sku_code"] = sku.code

        result.append(m)

    # сортировка: сначала есть расхождения
    result.sort(key=lambda x: (x["diff_qty"] != 0 or abs(x["diff_amount"]) > 0.0001, x["date"]), reverse=True)
    return result


@router.post("/approve")
def approve_final(
    store_id: int,
    sku_id: int,
    on_date: date,
    source: str = Query(pattern="^(promoter|network)$", description="Источник истины"),
    db: Session = Depends(get_db),
    _super=Depends(require_super),
):
    """
    Апрув строки сверки в SalesFinal из выбранного источника:
    - source=promoter: взять сумму из PromoterSale
    - source=network:  взять сумму из SalesNetwork
    Upsert по уникальному ключу (store_id, sku_id, date).
    """
    if source == "promoter":
        agg = (
            db.query(
                func.sum(PromoterSale.qty).label("qty"),
                func.sum(func.coalesce(PromoterSale.amount, 0)).label("amount"),
            )
            .filter(
                PromoterSale.store_id == store_id,
                PromoterSale.sku_id == sku_id,
                PromoterSale.sold_at == on_date,
            )
            .one()
        )
    else:
        agg = (
            db.query(
                func.sum(SalesNetwork.qty).label("qty"),
                func.sum(SalesNetwork.amount).label("amount"),
            )
            .filter(
                SalesNetwork.store_id == store_id,
                SalesNetwork.sku_id == sku_id,
                SalesNetwork.sold_at == on_date,
            )
            .one()
        )

    qty = int(agg.qty or 0)
    amount = float(agg.amount or 0.0)

    # upsert в SalesFinal
    row = (
        db.query(SalesFinal)
        .filter(
            SalesFinal.store_id == store_id,
            SalesFinal.sku_id == sku_id,
            SalesFinal.date == on_date,
        )
        .first()
    )
    if row is None:
        row = SalesFinal(
            store_id=store_id,
            sku_id=sku_id,
            date=on_date,
            qty=qty,
            amount=amount,
            source=source,
        )
        db.add(row)
    else:
        row.qty = qty
        row.amount = amount
        row.source = source

    db.commit()
    db.refresh(row)

    return {
        "ok": True,
        "final": {
            "store_id": row.store_id,
            "sku_id": row.sku_id,
            "date": row.date.isoformat(),
            "qty": row.qty,
            "amount": float(row.amount),
            "source": row.source,
        },
    }
