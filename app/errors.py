from flask import render_template, current_app


def register_error_handlers(app):
    """Register error handlers with the Flask app."""

    @app.errorhandler(404)
    def not_found_error(error):
        current_app.logger.warning(f"404 error: {error}")
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        current_app.logger.error(f"500 error: {error}")
        return render_template("errors/500.html"), 500
