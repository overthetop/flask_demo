"""Application configuration.

Loads environment variables from `.env` (via python-dotenv) and exposes a
simple `Config` object consumed by the app factory.
"""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration for the application.

    - `SECRET_KEY` should be explicitly set in non-dev environments; the
      fallback is only suitable for local development and will rotate on each
      process start (invalidating sessions).
    - `DATABASE_URL` defaults to the docker-compose dev database.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DATABASE_URL = (
        os.environ.get("DATABASE_URL")
        or "postgresql://postgres:postgres@localhost:5432/flask_showcase"
    )
