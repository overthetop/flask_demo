"""Application configuration with validation."""

import logging
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Flask configuration loaded from environment variables with sensible defaults."""

    # Core settings
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/flask_showcase",
    )

    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    _secure = os.environ.get("SESSION_COOKIE_SECURE", "false").lower()
    SESSION_COOKIE_SECURE = _secure in ("1", "true", "yes")

    @classmethod
    def validate(cls) -> None:
        """Validate and set defaults for required configuration."""
        # Handle SECRET_KEY
        if not cls.SECRET_KEY:
            env = os.environ.get("FLASK_ENV", "development")
            if env == "production":
                raise ValueError("SECRET_KEY must be set in production")
            cls.SECRET_KEY = secrets.token_hex(32)
            logger.warning(
                "SECRET_KEY not set - using random value (development only). "
                "Sessions will be lost on restart."
            )

        # Log configuration (without secrets)
        logger.info(f"Database: {cls.DATABASE_URL.split('@')[-1]}")  # Hide credentials
        logger.info(f"Secure cookies: {cls.SESSION_COOKIE_SECURE}")
