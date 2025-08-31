import logging
from flask import Flask
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    if not app.debug:
        # Remove default handlers to avoid duplicate logs
        app.logger.handlers.clear()

        # Create a formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create a handler for stdout
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)  # Set to desired level (INFO, WARNING, ERROR)

        # Add handler to app logger
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)  # Set to desired level

        # Prevent Flask from adding its own handlers
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
