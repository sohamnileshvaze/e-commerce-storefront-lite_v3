import sqlite3

from fastapi import APIRouter, Depends

from app.core.logger import logger
from app.db.connection import get_db
from app.models.schemas import DashboardSummary
from app.routes.auth import get_current_user
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    conn: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DashboardSummary:
    """Return the authenticated user dashboard metrics summary."""
    user_id = current_user["id"]
    cursor = conn.cursor()

    total_products = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0] or 0
    total_orders = cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)).fetchone()[0] or 0
    pending_orders = cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND order_status = 'pending'", (user_id,)
    ).fetchone()[0] or 0
    shipped_orders = cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND order_status = 'shipped'", (user_id,)
    ).fetchone()[0] or 0
    total_spent = cursor.execute(
        "SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE user_id = ? AND order_status != 'cancelled'",
        (user_id,),
    ).fetchone()[0] or 0.0

    summary = DashboardSummary(
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        shipped_orders=shipped_orders,
        total_spent=total_spent,
    )
    logger.info(
        "dashboard_summary user=%s total_products=%s total_orders=%s pending=%s shipped=%s total_spent=%s",
        user_id,
        total_products,
        total_orders,
        pending_orders,
        shipped_orders,
        total_spent,
    )
    return summary
