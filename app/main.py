import logging
import os

from fastapi import CORSMiddleware
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.logger import configure_logger, logger as configured_logger
from app.db.connection import init_db, path_from_database_url
from app.routes import auth as auth_routes
from app.routes import dashboard as dashboard_routes
from app.routes import orders as order_routes
from app.routes import products as product_routes

logger: logging.Logger = configured_logger

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
static_dir_valid = static_dir.startswith(f"{package_root}{os.sep}")

app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(order_routes.router)
app.include_router(dashboard_routes.router)


@app.on_event('startup')
async def on_startup():
    """Configure logging, initialize the database, and mount static assets."""
    configured = configure_logger()
    global logger
    logger = configured

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

    static_already_mounted = getattr(app.state, '_static_mounted', False)
    static_dir_exists = os.path.isdir(static_dir)

    if static_already_mounted:
        logger.debug('Static files already mounted; skipping republish at %s', static_dir)
    elif static_dir_valid and static_dir_exists:
        app.mount('/', StaticFiles(directory=static_dir, html=True), name='static')
        app.state._static_mounted = True
        logger.info('Static files mounted at / from %s', static_dir)
    else:
        logger.warning(
            'Static files not mounted: valid=%s exists=%s path=%s',
            static_dir_valid,
            static_dir_exists,
            static_dir,
        )


@app.on_event('shutdown')
async def on_shutdown():
    """Log shutdown events."""
    logger.info('Shutting down')


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return JSON responses for HTTP exceptions."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
