"""Database helpers."""

import psycopg
from flask import current_app, g
from psycopg.rows import dict_row


def get_db():
    """Get or create request-scoped database connection."""
    if "db" not in g:
        g.db = psycopg.connect(
            current_app.config["DATABASE_URL"],
            row_factory=dict_row,
        )
    return g.db


def close_db(e=None):
    """Close the database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Register database teardown handler."""
    app.teardown_appcontext(close_db)
