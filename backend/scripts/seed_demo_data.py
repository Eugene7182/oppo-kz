"""Seed deterministic demo data for OPPO KZ platform."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable
import calendar

from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.bonus import BonusRule, BonusScheme, BonusSchemeStatus, BonusSelectorType
from app.models.city import City
from app.models.network import Network
from app.models.period import ClosedPeriod, ClosedScope
from app.models.plan import PlanPromoterMonth, PlanSource
from app.models.product import Product, ProductStatus
from app.models.region import Region
from app.models.sale import Sale, SaleStatus
from app.models.store import Store
from app.models.user import User, UserRole, UserStatus

DATA_PATH_DEFAULT = Path("ops/demo/demo_data.json")


@dataclass(slots=True)
class SeedConfig:
    reference_date: date
    password: str
    payload: dict[str, Any]


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def month_add(value: date, offset: int) -> date:
    """Shift a date by `offset` months preserving the day when possible."""

    month = value.month - 1 + offset
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def build_anchors(reference: date) -> dict[str, date]:
    """Compute reusable anchor dates for seed specification."""

    current_week_start = reference - timedelta(days=reference.weekday())
    anchors = {
        "reference_date": reference,
        "today": reference,
        "current_week_start": current_week_start,
        "last_week_start": current_week_start - timedelta(days=7),
        "two_weeks_ago_start": current_week_start - timedelta(days=14),
    }
    current_month_start = reference.replace(day=1)
    anchors["current_month_start"] = current_month_start
    anchors["previous_month_start"] = month_add(current_month_start, -1)
    anchors["two_months_ago_start"] = month_add(current_month_start, -2)
    anchors["current_month_start_last_year"] = month_add(current_month_start, -12)
    anchors["previous_month_start_last_year"] = month_add(anchors["previous_month_start"], -12)
    return anchors


def resolve_date(spec: dict[str, Any] | None, anchors: dict[str, date]) -> date | None:
    """Resolve a date spec of the form {"anchor": name, "offset_days": int}."""

    if not spec:
        return None
    anchor_name = spec.get("anchor")
    if not anchor_name:
        raise ValueError("Date spec missing anchor")
    if anchor_name not in anchors:
        raise ValueError(f"Unknown anchor '{anchor_name}' in seed data")
    offset = int(spec.get("offset_days", 0))
    return anchors[anchor_name] + timedelta(days=offset)


def to_timestamp(d: date | None) -> datetime | None:
    """Convert date to UTC midnight timestamp."""

    if d is None:
        return None
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def ensure_region(session: Session, *, region_id: str, name: str) -> Region:
    region = session.get(Region, region_id)
    if region:
        region.name = name
    else:
        region = Region(id=region_id, name=name)
        session.add(region)
    return region


def ensure_city(session: Session, *, city_id: str, region_id: str, name: str) -> City:
    city = session.get(City, city_id)
    if city:
        city.name = name
        city.region_id = region_id
    else:
        city = City(id=city_id, name=name, region_id=region_id)
        session.add(city)
    return city


def ensure_network(session: Session, *, network_id: str, name: str) -> Network:
    network = session.get(Network, network_id)
    if network:
        network.name = name
    else:
        network = Network(id=network_id, name=name)
        session.add(network)
    return network


def ensure_store(
    session: Session,
    *,
    store_id: str,
    network_id: str,
    region_id: str,
    code: str,
    name: str,
    address: str | None = None,
) -> Store:
    store = session.get(Store, store_id)
    if store:
        store.network_id = network_id
        store.region_id = region_id
        store.code = code
        store.name = name
        store.address = address
    else:
        store = Store(
            id=store_id,
            network_id=network_id,
            region_id=region_id,
            code=code,
            name=name,
            address=address,
            active=True,
        )
        session.add(store)
    return store


def ensure_product(
    session: Session,
    *,
    product_id: str,
    sku: str,
    name: str,
    status: str,
    price: Decimal | None,
    attrs: dict[str, Any] | None,
    valid_from: date | None,
    valid_to: date | None,
) -> Product:
    product = session.get(Product, product_id)
    status_enum = ProductStatus(status)
    if product:
        product.sku = sku
        product.name = name
        product.status = status_enum
        product.price = price
        product.attrs_json = attrs
        product.valid_from = to_timestamp(valid_from)
        product.valid_to = to_timestamp(valid_to)
    else:
        product = Product(
            id=product_id,
            sku=sku,
            name=name,
            status=status_enum,
            price=price,
            attrs_json=attrs,
            valid_from=to_timestamp(valid_from),
            valid_to=to_timestamp(valid_to),
        )
        session.add(product)
    return product


def ensure_user(
    session: Session,
    *,
    user_id: str,
    email: str,
    full_name: str,
    role: str,
    region_id: str | None,
    password: str,
) -> User:
    hashed = get_password_hash(password)
    role_enum = UserRole(role)
    user = session.get(User, user_id)
    if user:
        user.email = email
        user.full_name = full_name
        user.role = role_enum
        user.region_id = region_id
        user.status = UserStatus.active
        user.hashed_password = hashed
    else:
        user = User(
            id=user_id,
            email=email,
            full_name=full_name,
            role=role_enum,
            region_id=region_id,
            status=UserStatus.active,
            hashed_password=hashed,
        )
        session.add(user)
    return user


def ensure_bonus_scheme(
    session: Session,
    *,
    scheme_id: str,
    network_id: str,
    valid_from: date,
    valid_to: date | None,
    status: str,
    rules: Iterable[dict[str, Any]],
) -> BonusScheme:
    scheme = session.get(BonusScheme, scheme_id)
    status_enum = BonusSchemeStatus(status)
    if scheme:
        scheme.network_id = network_id
        scheme.valid_from = valid_from
        scheme.valid_to = valid_to
        scheme.status = status_enum
    else:
        scheme = BonusScheme(
            id=scheme_id,
            network_id=network_id,
            valid_from=valid_from,
            valid_to=valid_to,
            status=status_enum,
        )
        session.add(scheme)
        session.flush()
    session.execute(delete(BonusRule).where(BonusRule.scheme_id == scheme.id))
    for rule in rules:
        session.add(
            BonusRule(
                scheme_id=scheme.id,
                selector_type=BonusSelectorType(rule["selector_type"]),
                selector_value=rule.get("selector_value"),
                amount=Decimal(str(rule["amount"])),
                conditions_json=rule.get("conditions"),
            )
        )
    return scheme


def ensure_plan(
    session: Session,
    *,
    period_ym: str,
    promoter_id: str,
    store_id: str | None,
    target_units: int | None,
    target_revenue: Decimal | None,
    updated_by: str,
) -> PlanPromoterMonth:
    plan = (
        session.execute(
            select(PlanPromoterMonth)
            .where(
                PlanPromoterMonth.period_ym == period_ym,
                PlanPromoterMonth.promoter_id == promoter_id,
                PlanPromoterMonth.store_id == store_id,
            )
        )
        .scalars()
        .first()
    )
    if plan:
        plan.target_units = target_units
        plan.target_revenue = target_revenue
        plan.source = PlanSource.import_file
        plan.version = max(plan.version, 1)
        plan.updated_by = updated_by
        plan.updated_at = datetime.now(timezone.utc)
    else:
        plan = PlanPromoterMonth(
            period_ym=period_ym,
            promoter_id=promoter_id,
            store_id=store_id,
            target_units=target_units,
            target_revenue=target_revenue,
            source=PlanSource.import_file,
            updated_by=updated_by,
        )
        session.add(plan)
    return plan


def ensure_sale(
    session: Session,
    *,
    sale_id: str,
    promoter_id: str,
    store_id: str,
    sku_id: str,
    qty: int,
    price: Decimal,
    sale_date: date,
    locked: bool,
) -> Sale:
    sale = session.get(Sale, sale_id)
    now = datetime.now(timezone.utc)
    if sale:
        sale.promoter_id = promoter_id
        sale.store_id = store_id
        sale.sku_id = sku_id
        sale.qty = qty
        sale.price = price
        sale.date = sale_date
        sale.status = SaleStatus.active
        sale.locked_at = now if locked else None
        sale.updated_at = now
    else:
        sale = Sale(
            id=sale_id,
            promoter_id=promoter_id,
            store_id=store_id,
            sku_id=sku_id,
            qty=qty,
            price=price,
            date=sale_date,
            status=SaleStatus.active,
            version=1,
            locked_at=now if locked else None,
            created_at=now,
            updated_at=now,
        )
        session.add(sale)
    return sale


def ensure_closed_period(
    session: Session,
    *,
    period_id: str,
    scope: ClosedScope,
    scope_id: str | None,
    from_date: date,
    to_date: date,
    created_by: str | None,
) -> ClosedPeriod:
    period = session.get(ClosedPeriod, period_id)
    now = datetime.now(timezone.utc)
    if period:
        period.scope = scope
        period.scope_id = scope_id
        period.from_date = from_date
        period.to_date = to_date
        period.created_by = created_by
    else:
        period = ClosedPeriod(
            id=period_id,
            scope=scope,
            scope_id=scope_id,
            from_date=from_date,
            to_date=to_date,
            created_by=created_by,
            created_at=now,
        )
        session.add(period)
    return period


# ---------------------------------------------------------------------------
# Inventory helpers
# ---------------------------------------------------------------------------

def stock_table_exists(session: Session) -> bool:
    row = session.execute(text("select to_regclass('public.stock_balances') is not null")).scalar()
    return bool(row)


def upsert_inventory(session: Session, items: list[dict[str, Any]]) -> None:
    if not items or not stock_table_exists(session):
        return
    for store_id in {int(item["store_key_numeric"]) for item in items}:
        session.execute(text("delete from stock_balances where store_id = :store_id"), {"store_id": store_id})
    for item in items:
        session.execute(
            text(
                """
                insert into stock_balances (store_id, sku_id, on_hand, in_transit)
                values (:store_id, :sku_id, :on_hand, :in_transit)
                """
            ),
            {
                "store_id": int(item["store_key_numeric"]),
                "sku_id": int(item["sku_key_numeric"]),
                "on_hand": float(item.get("on_hand", 0)),
                "in_transit": float(item.get("in_transit", 0)),
            },
        )


# ---------------------------------------------------------------------------
# Purge
# ---------------------------------------------------------------------------

def purge_existing(session: Session, data: dict[str, Any]) -> None:
    sale_ids = [sale["id"] for sale in data.get("sales", [])]
    if sale_ids:
        session.execute(delete(Sale).where(Sale.id.in_(sale_ids)))
    scheme_ids = [scheme["id"] for scheme in data.get("bonus_schemes", [])]
    if scheme_ids:
        session.execute(delete(BonusScheme).where(BonusScheme.id.in_(scheme_ids)))
    plan_promoters = [item["promoter_key"] for item in data.get("plans", [])]
    if plan_promoters:
        session.execute(delete(PlanPromoterMonth).where(PlanPromoterMonth.promoter_id.in_(plan_promoters)))
    user_ids = [user["id"] for user in data.get("users", [])]
    if user_ids:
        session.execute(delete(User).where(User.id.in_(user_ids)))
    store_ids = [store["id"] for network in data.get("networks", []) for store in network.get("stores", [])]
    if store_ids:
        session.execute(delete(Store).where(Store.id.in_(store_ids)))
    network_ids = [network["id"] for network in data.get("networks", [])]
    if network_ids:
        session.execute(delete(Network).where(Network.id.in_(network_ids)))
    city_ids = [city["id"] for region in data.get("regions", []) for city in region.get("cities", [])]
    if city_ids:
        session.execute(delete(City).where(City.id.in_(city_ids)))
    region_ids = [region["id"] for region in data.get("regions", [])]
    if region_ids:
        session.execute(delete(Region).where(Region.id.in_(region_ids)))
    product_ids = [product["id"] for product in data.get("products", [])]
    if product_ids:
        session.execute(delete(Product).where(Product.id.in_(product_ids)))
    period_ids = [period["id"] for period in data.get("closed_periods", [])]
    if period_ids:
        session.execute(delete(ClosedPeriod).where(ClosedPeriod.id.in_(period_ids)))


# ---------------------------------------------------------------------------
# Main seeding logic
# ---------------------------------------------------------------------------

def apply_seed(session: Session, config: SeedConfig) -> None:
    data = config.payload
    anchors = build_anchors(config.reference_date)

    # Regions and cities
    key_to_region = {region["key"]: region["id"] for region in data.get("regions", [])}
    for region_data in data.get("regions", []):
        region = ensure_region(session, region_id=region_data["id"], name=region_data["name"])
        for city in region_data.get("cities", []):
            ensure_city(session, city_id=city["id"], region_id=region.id, name=city["name"])

    # Networks and stores
    for network in data.get("networks", []):
        ensure_network(session, network_id=network["id"], name=network["name"])
        for store in network.get("stores", []):
            ensure_store(
                session,
                store_id=store["id"],
                network_id=network["id"],
                region_id=key_to_region[store["region_key"]],
                code=store["code"],
                name=store["name"],
                address=store.get("address"),
            )

    # Products
    for product in data.get("products", []):
        ensure_product(
            session,
            product_id=product["id"],
            sku=product["sku"],
            name=product["name"],
            status=product["status"],
            price=Decimal(str(product.get("price"))) if product.get("price") is not None else None,
            attrs=product.get("attrs"),
            valid_from=resolve_date(product.get("valid_from"), anchors),
            valid_to=resolve_date(product.get("valid_to"), anchors),
        )

    # Users
    for user in data.get("users", []):
        region_id = key_to_region.get(user.get("region_key")) if user.get("region_key") else None
        ensure_user(
            session,
            user_id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            region_id=region_id,
            password=config.password,
        )

    # Bonus schemes
    for scheme in data.get("bonus_schemes", []):
        ensure_bonus_scheme(
            session,
            scheme_id=scheme["id"],
            network_id=next(n["id"] for n in data["networks"] if n["key"] == scheme["network_key"]),
            valid_from=resolve_date(scheme.get("valid_from"), anchors) or config.reference_date,
            valid_to=resolve_date(scheme.get("valid_to"), anchors),
            status=scheme["status"],
            rules=scheme.get("rules", []),
        )

    # Plans
    promoter_ids = {user["key"]: user["id"] for user in data.get("users", [])}
    store_ids = {store["key"]: store["id"] for network in data.get("networks", []) for store in network.get("stores", [])}
    admin_id = promoter_ids.get("user_admin")
    for plan in data.get("plans", []):
        period_start = month_add(config.reference_date.replace(day=1), plan.get("period_offset_months", 0))
        period_ym = period_start.strftime("%Y-%m")
        ensure_plan(
            session,
            period_ym=period_ym,
            promoter_id=promoter_ids[plan["promoter_key"]],
            store_id=store_ids.get(plan.get("store_key")),
            target_units=plan.get("target_units"),
            target_revenue=Decimal(str(plan.get("target_revenue"))) if plan.get("target_revenue") is not None else None,
            updated_by=admin_id or promoter_ids[plan["promoter_key"]],
        )

    # Sales
    product_ids = {product["key"]: product["id"] for product in data.get("products", [])}
    for sale in data.get("sales", []):
        ensure_sale(
            session,
            sale_id=sale["id"],
            promoter_id=promoter_ids[sale["promoter_key"]],
            store_id=store_ids[sale["store_key"]],
            sku_id=product_ids[sale["sku_key"]],
            qty=int(sale["qty"]),
            price=Decimal(str(sale["price"])),
            sale_date=resolve_date(sale.get("date"), anchors) or config.reference_date,
            locked=bool(sale.get("locked", False)),
        )

    # Closed periods (optional)
    for period in data.get("closed_periods", []):
        scope = ClosedScope(period["scope"])
        scope_id = None
        if period.get("scope_key"):
            if scope == ClosedScope.region:
                scope_id = key_to_region[period["scope_key"]]
            elif scope == ClosedScope.store:
                scope_id = store_ids[period["scope_key"]]
        ensure_closed_period(
            session,
            period_id=period["id"],
            scope=scope,
            scope_id=scope_id,
            from_date=resolve_date(period.get("from"), anchors) or config.reference_date,
            to_date=resolve_date(period.get("to"), anchors) or config.reference_date,
            created_by=admin_id,
        )

    # Inventory (legacy numeric ids)
    upsert_inventory(session, data.get("inventory", []))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_config(path: Path) -> SeedConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    reference = date.fromisoformat(payload["reference_date"])
    return SeedConfig(reference_date=reference, password=payload["password"], payload=payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo data")
    parser.add_argument("--data-path", type=Path, default=DATA_PATH_DEFAULT, help="Path to JSON dataset")
    parser.add_argument("--purge", action="store_true", help="Remove existing seed rows before inserting")
    args = parser.parse_args()

    config = load_config(args.data_path)
    with SessionLocal() as session:
        if args.purge:
            purge_existing(session, config.payload)
            session.commit()
        apply_seed(session, config)
        session.commit()
    print("Seed completed", config.reference_date.isoformat())


if __name__ == "__main__":
    main()
