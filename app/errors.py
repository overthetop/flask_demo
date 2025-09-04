"""Custom error handlers.

Provides simple, user-friendly pages for common HTTP errors while logging at
appropriate levels for observability.
"""

from flask import current_app, render_template


def register_error_handlers(app):
    """Attach error handlers for 404 and 500 to the app instance."""

    @app.errorhandler(404)
    def not_found_error(error):
        current_app.logger.warning(f"404 error: {error}")
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        current_app.logger.error(f"500 error: {error}")
        return render_template("errors/500.html"), 500
