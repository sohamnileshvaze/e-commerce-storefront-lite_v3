import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.logger import logger
from app.db.connection import get_db
from app.models.schemas import ProductListResponse, ProductOut
from app.repositories.product_repository import ProductRepository

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(price|created_at)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: sqlite3.Connection = Depends(get_db),
) -> ProductListResponse:
    """List products with optional filters, sorting, and pagination."""
    products, total = ProductRepository().search_products(
        conn, search, category, min_price, max_price, sort_by, page, page_size
    )
    if total is None:
        total = 0
    items = [ProductOut(**product) for product in products]
    logger.info(
        "list_products search=%s category=%s min_price=%s max_price=%s sort_by=%s page=%s page_size=%s returned=%s total=%s",
        search,
        category,
        min_price,
        max_price,
        sort_by,
        page,
        page_size,
        len(items),
        total,
    )
    return ProductListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/{id}", response_model=ProductOut)
def get_product(id: int, conn: sqlite3.Connection = Depends(get_db)) -> ProductOut:
    """Retrieve a single product by its identifier."""
    product_record = ProductRepository().get_product(conn, id)
    if not product_record:
        logger.info("get_product id=%s status=not_found", id)
        raise HTTPException(status_code=404, detail="Product not found")
    product = ProductOut(**product_record)
    logger.info("get_product id=%s status=fetched", id)
    return product
