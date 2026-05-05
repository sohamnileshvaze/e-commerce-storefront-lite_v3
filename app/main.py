"""Application entry point and wiring.

This module mounts the frontend static at '/' and registers API routers under the '/api' prefix.
"""

import inspect
import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logger import configure_logger, logger
from app.db.connection import init_db, path_from_database_url
from app.routes import auth as auth_routes
from app.routes import dashboard as dashboard_routes
from app.routes import orders as order_routes
from app.routes import products as product_routes

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
static_dir_real = os.path.realpath(static_dir)
package_root_real = os.path.realpath(os.path.dirname(__file__))
if not static_dir_real.startswith(package_root_real + os.sep) and static_dir_real != package_root_real:
    raise RuntimeError(
        f"Refusing to mount static directory outside package root: {static_dir!r}"
    )
if not os.path.isdir(static_dir):
    raise RuntimeError(
        f"Static directory not found at {static_dir!r}. Repo is expected to include app/static per project spec."
    )
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
logger.info("Static files mounted at / from %s", os.path.abspath(static_dir))  # Iteration 4 fix: module-level static mount per spec

API_PREFIX = "/api"  # Iteration 4 fix: keep API routes under /api to avoid root-level static collisions
app.include_router(auth_routes.router, prefix=API_PREFIX)
app.include_router(product_routes.router, prefix=API_PREFIX)
app.include_router(order_routes.router, prefix=API_PREFIX)
app.include_router(dashboard_routes.router, prefix=API_PREFIX)


@app.on_event('startup')
async def on_startup():
    """Configure logging and initialize the database."""
    configure_logger()

    logger.info('Starting application')

    try:
        db_path = path_from_database_url(settings.DATABASE_URL)
        logger.debug('Database resolved to path: %s', db_path)
    except Exception:
        logger.debug('path_from_database_url failed; continuing', exc_info=True)

    try:
        if inspect.iscoroutinefunction(init_db):
            await init_db()
        else:
            await run_in_threadpool(init_db)
    except Exception:
        logger.exception('Database initialization failed')
        raise

    # Static files are mounted at import time per spec; no runtime remount needed.


@app.on_event('shutdown')
async def on_shutdown():
    """Log shutdown events."""
    logger.info('Shutting down')


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return JSON responses for HTTP exceptions."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
