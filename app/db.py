"""Database helpers.

This module manages a single psycopg2 connection per request context via
`flask.g` and provides helpers to open/close the connection gracefully.
Schema initialization is intentionally not handled here; run `init-db.sql`
manually against the database to create tables.
"""

import psycopg2
from flask import current_app, g
from psycopg2.extras import RealDictCursor


def get_db():
    """Get a request-scoped database connection.

    Returns the same connection for the lifetime of the request, creating it
    on first access. Rows are returned as dict-like objects via
    `RealDictCursor` for readability in templates and JSON responses.
    """
    if "db" not in g:
        database_url = current_app.config["DATABASE_URL"]
        current_app.logger.debug(f"Connecting to database: {database_url}")
        g.db = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return g.db


def close_db(e=None):
    """Close the connection stored in `g`, if any."""
    db = g.pop("db", None)
    if db is not None:
        current_app.logger.debug("Closing database connection")
        db.close()


def init_app(app):
    """Register teardown on the Flask app.

    Note: DB schema initialization is out of scope here by design.
    """
    app.teardown_appcontext(close_db)
