"""Foundation utilities providing exception handlers and configuration helpers.

Required environment variables:
- JWT_SECRET_KEY (ensures security helpers can sign tokens).
Example .env contents:
JWT_SECRET_KEY=supersecret
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return a JSON response that mirrors the HTTPException detail."""

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
