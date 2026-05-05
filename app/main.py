import logging
import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.logger import configure_logger, logger as configured_logger
from app.db.connection import init_db
from app.routes import auth as auth_routes
from app.routes import products as product_routes
from app.routes import orders as order_routes
from app.routes import dashboard as dashboard_routes

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
if not static_dir.startswith(package_root + os.sep):
    raise RuntimeError(f"Static directory {static_dir!r} is outside the package root {package_root!r}")
if not os.path.isdir(static_dir):
    logger.warning("Static directory %s does not exist. Static files will return 404s.", static_dir)

app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(order_routes.router)
app.include_router(dashboard_routes.router)


@app.on_event('startup')
async def on_startup():
    """Configure logging and initialize the database on startup."""
    configure_logger()
    logger.info('Starting application')
    try:
        init_db()
    except Exception:
        logger.exception('Database initialization failed')
        raise


@app.on_event('shutdown')
async def on_shutdown():
    """Log shutdown events."""
    logger.info('Shutting down')


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return JSON responses for HTTP exceptions."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
