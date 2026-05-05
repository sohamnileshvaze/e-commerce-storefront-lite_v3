import logging
import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.logger import configure_logger, logger as configured_logger
from app.db.connection import init_db, path_from_database_url
from app.routes import auth as auth_routes
from app.routes import dashboard as dashboard_routes
from app.routes import orders as order_routes
from app.routes import products as product_routes

logger: logging.Logger = configured_logger  # Iteration 4 fix: single module-level logger reference avoids confusion

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
package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
static_dir_valid = os.path.abspath(static_dir).startswith(f"{package_root}{os.sep}")
static_dir_exists = os.path.isdir(static_dir)
static_can_mount = static_dir_valid and static_dir_exists

if static_can_mount:
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info("Static files mounted at / from %s", os.path.abspath(static_dir))  # Iteration 4 fix: module-level static mount per spec
else:
    logger.warning(
        "Static files not mounted: valid=%s exists=%s path=%s",
        static_dir_valid,
        static_dir_exists,
        static_dir,
    )

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
