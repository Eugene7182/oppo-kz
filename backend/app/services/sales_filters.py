from __future__ import annotations

"""Helpers to build sales queries with filters."""

from typing import Any, Dict

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.sales_promoters import SalesPromoter
from app.models.sales_retail import SalesRetail
from app.models.store import Store


def build_promoter_query(db: Session, filters: Dict[str, Any]) -> Select:
    """Return SELECT for promoter sales with applied filters."""

    stmt = select(SalesPromoter).join(Store, SalesPromoter.store_id == Store.id)
    if filters.get("store_id"):
        stmt = stmt.where(SalesPromoter.store_id == filters["store_id"])
    if filters.get("sku_id"):
        stmt = stmt.where(SalesPromoter.sku_id == filters["sku_id"])
    if filters.get("promoter_id"):
        stmt = stmt.where(SalesPromoter.promoter_id == filters["promoter_id"])
    if filters.get("approved") is not None:
        stmt = stmt.where(SalesPromoter.approved_by_office == filters["approved"])
    if filters.get("date_from"):
        stmt = stmt.where(SalesPromoter.sold_at >= filters["date_from"])
    if filters.get("date_to"):
        stmt = stmt.where(SalesPromoter.sold_at <= filters["date_to"])
    if filters.get("network_id"):
        stmt = stmt.where(Store.network_id == filters["network_id"])
    if filters.get("region_id"):
        stmt = stmt.where(Store.region_id == filters["region_id"])
    return stmt


def build_retail_query(db: Session, filters: Dict[str, Any]) -> Select:
    """Return SELECT for retail sales with applied filters."""

    stmt = select(SalesRetail).join(Store, SalesRetail.store_id == Store.id)
    if filters.get("store_id"):
        stmt = stmt.where(SalesRetail.store_id == filters["store_id"])
    if filters.get("sku_id"):
        stmt = stmt.where(SalesRetail.sku_id == filters["sku_id"])
    if filters.get("date_from"):
        stmt = stmt.where(SalesRetail.sold_at >= filters["date_from"])
    if filters.get("date_to"):
        stmt = stmt.where(SalesRetail.sold_at <= filters["date_to"])
    if filters.get("feed_batch_id"):
        stmt = stmt.where(SalesRetail.feed_batch_id == filters["feed_batch_id"])
    if filters.get("network_id"):
        stmt = stmt.where(Store.network_id == filters["network_id"])
    if filters.get("region_id"):
        stmt = stmt.where(Store.region_id == filters["region_id"])
    return stmt


__all__ = ["build_promoter_query", "build_retail_query"]
