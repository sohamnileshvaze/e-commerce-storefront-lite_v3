"""Configure application logging without exposing JWT_SECRET_KEY or credentials.

Required environment variables:
- JWT_SECRET_KEY (used for security helpers, but never logged).
Example .env contents:
JWT_SECRET_KEY=supersecret
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from .config import get_settings


def configure_logger() -> logging.Logger:
    """Return a logger that writes to rotating file and console handlers."""

    settings = get_settings()
    logger = logging.getLogger(settings.APP_NAME)
    if logger.handlers:
        return logger

    level = logging.DEBUG if settings.ENV == "development" else logging.INFO
    logger.setLevel(level)

    os.makedirs("./logs", exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = RotatingFileHandler("./logs/app.log", maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = configure_logger()
