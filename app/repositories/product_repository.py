import sqlite3
from typing import Dict, List, Optional, Tuple

from app.core.logger import logger
from app.db.connection import get_db
from app.models.schemas import OrderOut, ProductOut, UserOut


class ProductRepository:
    """Data access layer for product catalog entries."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._connection_provider = get_db

    def get_product(self, conn: sqlite3.Connection, product_id: int) -> Optional[Dict]:
        """Return a product by id if it exists."""
        row = conn.execute(
            "SELECT id, name, description, category, price, stock_qty, image_url, created_at FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        if not row:
            return None
        record = dict(row)
        ProductOut(**record)
        return record

    def search_products(
        self,
        conn: sqlite3.Connection,
        search: Optional[str],
        category: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        sort_by: str,
        page: int,
        page_size: int,
    ) -> Tuple[List[Dict], int]:
        """Return paginated products list along with total count."""
        base_sql = "SELECT id, name, description, category, price, stock_qty, image_url, created_at FROM products WHERE 1=1"
        filter_sql_parts: List[str] = []
        params: List[Optional[object]] = []

        if search:
            like_value = f"%{search}%"
            filter_sql_parts.append("(name LIKE ? OR description LIKE ?)")
            params.extend([like_value, like_value])
        if category:
            filter_sql_parts.append("category = ?")
            params.append(category)
        if min_price is not None:
            filter_sql_parts.append("price >= ?")
            params.append(min_price)
        if max_price is not None:
            filter_sql_parts.append("price <= ?")
            params.append(max_price)

        filter_sql = ""
        if filter_sql_parts:
            filter_sql = "".join(f" AND {part}" for part in filter_sql_parts)

        if sort_by == "price":
            order_sql = " ORDER BY price ASC, created_at DESC"
        elif sort_by == "price_desc":
            order_sql = " ORDER BY price DESC, created_at DESC"
        elif sort_by == "created_at":
            order_sql = " ORDER BY created_at DESC"
        else:
            order_sql = " ORDER BY created_at DESC"

        offset = (page - 1) * page_size
        query_sql = f"{base_sql}{filter_sql}{order_sql} LIMIT ? OFFSET ?"
        query_params: List[object] = params + [page_size, offset]

        rows = conn.execute(query_sql, tuple(query_params)).fetchall()
        items: List[Dict] = []
        for row in rows:
            record = dict(row)
            ProductOut(**record)
            items.append(record)

        count_sql = f"SELECT COUNT(*) FROM products WHERE 1=1{filter_sql}"
        total = conn.execute(count_sql, tuple(params)).fetchone()[0]

        logger.debug("search_products filters=%s total=%s", filter_sql_parts, total)
        return items, total

    def create_product(
        self,
        conn: sqlite3.Connection,
        name: str,
        description: str,
        category: str,
        price: float,
        stock_qty: int,
        image_url: Optional[str],
    ) -> int:
        """Insert a new product and return its identifier."""
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, description, category, price, stock_qty, image_url) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, category, price, stock_qty, image_url),
        )
        return cursor.lastrowid
