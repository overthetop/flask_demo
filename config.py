"""Application configuration."""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Basic Flask configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/flask_showcase",
    )
