import sqlite3
from typing import Dict, List, Optional, Tuple

from app.core.logger import logger
from app.db.connection import get_db
from app.models.schemas import OrderOut, ProductOut, UserOut


class OrderRepository:
    """Data access layer for user orders and related product snapshots."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._connection_provider = get_db

    def create_order(
        self,
        conn: sqlite3.Connection,
        user_id: int,
        product_id: int,
        quantity: int,
        unit_price: float,
        order_status: str = "pending",
    ) -> int:
        """Create an order, validate stock, and deduct inventory transactionally."""
        cursor = conn.cursor()
        try:
            conn.execute("BEGIN")
            stock_row = cursor.execute(
                "SELECT stock_qty FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()
            if not stock_row or stock_row["stock_qty"] < quantity:
                raise ValueError("insufficient_stock")

            total_price = quantity * unit_price
            cursor.execute(
                "INSERT INTO orders (user_id, product_id, quantity, unit_price, total_price, order_status) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, product_id, quantity, unit_price, total_price, order_status),
            )
            order_id = cursor.lastrowid
            cursor.execute(
                "UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?",
                (quantity, product_id),
            )
            conn.commit()
            return order_id
        except Exception:
            conn.rollback()
            logger.exception("Failed to create order for user %s and product %s", user_id, product_id)
            raise

    def get_orders_for_user(
        self,
        conn: sqlite3.Connection,
        user_id: int,
        page: int,
        page_size: int,
    ) -> Tuple[List[Dict], int]:
        """Return paginated orders for a user with nested product data."""
        offset = (page - 1) * page_size
        query = """
            SELECT
              o.id,
              o.user_id,
              o.product_id,
              o.quantity,
              o.unit_price,
              o.total_price,
              o.order_status,
              o.created_at,
              p.id AS p_id,
              p.name AS p_name,
              p.description AS p_description,
              p.category AS p_category,
              p.price AS p_price,
              p.stock_qty AS p_stock_qty,
              p.image_url AS p_image_url,
              p.created_at AS p_created_at
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query, (user_id, page_size, offset)).fetchall()
        orders: List[Dict] = []
        for row in rows:
            product_payload = {
                "id": row["p_id"],
                "name": row["p_name"],
                "description": row["p_description"],
                "category": row["p_category"],
                "price": row["p_price"],
                "stock_qty": row["p_stock_qty"],
                "image_url": row["p_image_url"],
                "created_at": row["p_created_at"],
            }
            product = ProductOut(**product_payload)

            order_payload = {
                "id": row["id"],
                "user_id": row["user_id"],
                "product_id": row["product_id"],
                "quantity": row["quantity"],
                "unit_price": row["unit_price"],
                "total_price": row["total_price"],
                "order_status": row["order_status"],
                "created_at": row["created_at"],
                "product": product,
            }
            order_record = OrderOut(**order_payload)
            orders.append(order_record.dict())

        total = conn.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)).fetchone()[0]
        return orders, total

    def get_order_by_id(self, conn: sqlite3.Connection, order_id: int) -> Optional[Dict]:
        """Return a single order with nested product metadata."""
        query = """
            SELECT
              o.id,
              o.user_id,
              o.product_id,
              o.quantity,
              o.unit_price,
              o.total_price,
              o.order_status,
              o.created_at,
              p.id AS p_id,
              p.name AS p_name,
              p.description AS p_description,
              p.category AS p_category,
              p.price AS p_price,
              p.stock_qty AS p_stock_qty,
              p.image_url AS p_image_url,
              p.created_at AS p_created_at
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.id = ?
        """
        row = conn.execute(query, (order_id,)).fetchone()
        if not row:
            return None
        product_payload = {
            "id": row["p_id"],
            "name": row["p_name"],
            "description": row["p_description"],
            "category": row["p_category"],
            "price": row["p_price"],
            "stock_qty": row["p_stock_qty"],
            "image_url": row["p_image_url"],
            "created_at": row["p_created_at"],
        }
        product = ProductOut(**product_payload)
        order_payload = {
            "id": row["id"],
            "user_id": row["user_id"],
            "product_id": row["product_id"],
            "quantity": row["quantity"],
            "unit_price": row["unit_price"],
            "total_price": row["total_price"],
            "order_status": row["order_status"],
            "created_at": row["created_at"],
            "product": product,
        }
        order_record = OrderOut(**order_payload)
        return order_record.dict()
