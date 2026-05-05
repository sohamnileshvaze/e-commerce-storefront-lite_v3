"""Foundation configuration helpers.

Required environment variables:
- JWT_SECRET_KEY (must be set in environment or .env).
Example .env contents:
JWT_SECRET_KEY=supersecret
"""

from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):  # type: ignore[valid-type, misc]
    """Application settings loaded from environment variables."""

    APP_NAME: str = "E-Commerce Storefront Lite"
    ENV: str = Field("development")
    DATABASE_URL: str = Field("sqlite:///./ecommerce.db")
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()


def get_settings() -> Settings:
    """Return the cached Settings instance, raising ValidationError if JWT_SECRET_KEY is missing."""

    return settings
