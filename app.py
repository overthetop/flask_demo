"""Flask application - Development entrypoint.

This module contains the application factory and serves as the development
entrypoint. Run `python app.py` for local development or use `wsgi.py` for
production serving with Waitress.
"""

import logging
import os

from flask import Flask

from config import Config
from db import init_app
from errors import register_error_handlers
from routes import main


def setup_logging():
    """Configure simple structured logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_app():
    """Create and configure the Flask application."""
    setup_logging()

    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main)
    register_error_handlers(app)
    init_app(app)

    return app


app = create_app()

if __name__ == "__main__":
    debug_env = os.environ.get("FLASK_DEBUG") or os.environ.get("DEBUG")
    debug = str(debug_env).lower() in ("1", "true", "yes")
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=debug,
    )
