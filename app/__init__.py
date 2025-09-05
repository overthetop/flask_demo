"""Flask application factory and bootstrap.

This module exposes a single `create_app` function that configures the Flask
application, registers blueprints and error handlers, and wires up the
database integration. The factory pattern keeps the code testable and
environment‑agnostic.
"""

import logging

from flask import Flask

from app.config import Config


def create_app():
    """Create and configure an instance of the Flask application.

    - Loads configuration from environment via `Config`.
    - Sets up concise, production‑friendly logging when not in debug mode.
    - Registers routes, error handlers and database helpers.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging (keep concise in dev; structured in prod)
    if not app.debug and not app.testing:
        # Remove default handlers to avoid duplicate logs from Flask/werkzeug
        app.logger.handlers.clear()

        # Create a formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create a handler for stdout
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        # Stream to stdout; INFO is a sensible default for production
        handler.setLevel(logging.INFO)

        # Add handler to app logger
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

        # Prevent Flask from adding its own handlers and double‑logging
        app.logger.propagate = False

    # Register blueprints
    from app.routes import main

    app.register_blueprint(main)

    # Register error handlers
    from app.errors import register_error_handlers

    register_error_handlers(app)

    # Initialize database
    from app.db import init_app

    init_app(app)

    return app
