"""Product endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authz import require_roles
from app.core.security import get_db
from app.models.product import Product, ProductStatus
from app.models.user import User, UserRole
from app.schemas.product import ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    status_filter: ProductStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Product]:
    """Список SKU с опциональной фильтрацией по статусу."""

    query = db.query(Product)
    if status_filter:
        query = query.filter(Product.status == status_filter)
    products = (
        query.order_by(Product.name.asc()).offset(offset).limit(limit).all()
    )
    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)) -> Product:
    """Получить SKU по идентификатору."""

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin])),
) -> Product:
    """Обновить SKU (например, пометить как EOL)."""

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    data = payload.model_dump(exclude_unset=True, by_alias=False)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No changes provided")

    if "status" in data:
        product.status = data["status"]
    if "name" in data:
        product.name = data["name"]
    if "price" in data:
        product.price = data["price"]
    if "valid_to" in data:
        product.valid_to = data["valid_to"]

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


__all__ = ["router"]
