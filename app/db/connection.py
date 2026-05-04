import sqlite3
from pathlib import Path
from typing import Generator

from app.core.config import get_settings
from app.core.logger import logger
from fastapi import HTTPException

_SQLITE_URL_PREFIX = "sqlite:///"


def path_from_database_url(url: str) -> str:
    """Return the sqlite database file path for supported database URLs."""

    if not url.startswith(_SQLITE_URL_PREFIX):
        raise ValueError("Only sqlite:/// URLs are supported for DATABASE_URL")

    path = url[len(_SQLITE_URL_PREFIX) :]
    if not path:
        raise ValueError("DATABASE_URL must include a path component for sqlite")

    return path


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Open a sqlite3 connection configured with WAL and foreign key enforcement."""

    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    fk_row = conn.execute("PRAGMA foreign_keys;").fetchone()
    if not fk_row or fk_row[0] != 1:
        conn.close()
        raise sqlite3.OperationalError("Failed to enable foreign key enforcement")

    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a sqlite3 connection for FastAPI dependencies."""

    settings = get_settings()
    db_url = settings.DATABASE_URL
    try:
        db_path = path_from_database_url(db_url)
    except ValueError as exc:
        logger.exception("Invalid DATABASE_URL %s", db_url)
        raise HTTPException(status_code=500, detail="Invalid database configuration") from exc

    conn = get_db_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create the application tables and indexes if they do not yet exist."""

    settings = get_settings()
    db_url = settings.DATABASE_URL
    try:
        db_path = path_from_database_url(db_url)
    except ValueError as exc:
        logger.exception("Failed to parse DATABASE_URL %s", db_url)
        raise RuntimeError("Invalid DATABASE_URL") from exc

    logger.info("Initializing DB at %s", db_path)

    conn = None
    try:
        conn = get_db_connection(db_path)
        conn.execute("BEGIN")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              description TEXT NOT NULL,
              category TEXT NOT NULL,
              price REAL NOT NULL CHECK(price >= 0),
              stock_qty INTEGER NOT NULL DEFAULT 0 CHECK(stock_qty >= 0),
              image_url TEXT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              product_id INTEGER NOT NULL,
              quantity INTEGER NOT NULL CHECK(quantity > 0),
              unit_price REAL NOT NULL CHECK(unit_price >= 0),
              total_price REAL NOT NULL CHECK(total_price >= 0),
              order_status TEXT NOT NULL DEFAULT 'pending',
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
              FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """
        )

        conn.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at DESC);")

        conn.commit()
    except sqlite3.Error as exc:
        if conn:
            conn.rollback()
        logger.exception("Failed to initialize DB at %s", db_path)
        raise RuntimeError("Database initialization failed") from exc
    finally:
        if conn:
            conn.close()
