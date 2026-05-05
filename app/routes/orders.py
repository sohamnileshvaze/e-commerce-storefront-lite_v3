import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.logger import logger
from app.db.connection import get_db
from app.models.schemas import OrderOut
from app.repositories.order_repository import OrderRepository
from app.routes.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Return paged orders belonging to the authenticated user."""
    repo = OrderRepository()
    rows, total = repo.get_orders_for_user(conn, current_user["id"], page, page_size)
    if total is None:
        total = 0
    orders = [OrderOut(**row) for row in rows]
    logger.info(
        "list_orders page=%s page_size=%s returned=%s total=%s",
        page,
        page_size,
        len(orders),
        total,
    )
    return {
        "items": [order.dict() for order in orders],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/{id}", response_model=OrderOut)
def get_order(
    id: int,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> OrderOut:
    """Return the specified order when it belongs to the requesting user."""
    order_record = OrderRepository().get_order_by_id(conn, id)
    if not order_record:
        logger.info("get_order id=%s status=not_found", id)
        raise HTTPException(status_code=404, detail="Order not found")
    if order_record["user_id"] != current_user["id"]:
        logger.info("get_order id=%s status=forbidden", id)
        raise HTTPException(status_code=403, detail="Forbidden")
    order = OrderOut(**order_record)
    logger.info("get_order id=%s status=fetched", id)
    return order
