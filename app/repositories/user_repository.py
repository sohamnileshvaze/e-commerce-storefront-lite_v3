import sqlite3
from typing import Dict, List, Optional, Tuple

from app.core.logger import logger
from app.db.connection import get_db
from app.models.schemas import OrderOut, ProductOut, UserOut


class UserRepository:
    """Data access layer for application users."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._connection_provider = get_db

    def create_user(self, conn: sqlite3.Connection, name: str, email: str, password_hash: str) -> int:
        """Insert a new user and return the generated identifier."""
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            user_id = cursor.lastrowid
            if user_id is None:
                raise RuntimeError("Failed to retrieve new user id")
            return user_id
        except sqlite3.IntegrityError as exc:
            if "users.email" in str(exc):
                logger.debug("Duplicate user email detected: %s", email)
                raise ValueError("duplicate_email") from exc
            raise

    def get_user_by_email(self, conn: sqlite3.Connection, email: str) -> Optional[Dict]:
        """Retrieve a user along with their password hash."""
        row = conn.execute(
            "SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if not row:
            return None
        record = dict(row)
        user_payload = {key: record[key] for key in ("id", "name", "email", "created_at")}
        UserOut(**user_payload)
        return record

    def get_user_by_id(self, conn: sqlite3.Connection, user_id: int) -> Optional[Dict]:
        """Retrieve public user data that matches the UserOut schema."""
        row = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        record = dict(row)
        UserOut(**record)
        return record
