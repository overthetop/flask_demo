"""Database connection and transaction management."""

from collections.abc import Generator
from contextlib import contextmanager

import psycopg
from flask import Flask, current_app, g
from psycopg import Connection
from psycopg.rows import dict_row


def get_db() -> Connection:
    """Get or create request-scoped database connection.

    Returns:
        Connection: A psycopg connection with dict_row factory.

    Raises:
        psycopg.Error: If database connection fails.
    """
    if "db" not in g:
        try:
            g.db = psycopg.connect(
                current_app.config["DATABASE_URL"],
                row_factory=dict_row,
            )
        except psycopg.Error as e:
            current_app.logger.error(f"Database connection failed: {e}")
            raise
    return g.db


@contextmanager
def transaction() -> Generator[Connection, None, None]:
    """Context manager for database transactions with automatic commit/rollback.

    Usage:
        with transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users ...")
            # Automatically commits on success, rolls back on exception

    Yields:
        Connection: Database connection for the transaction.

    Raises:
        psycopg.Error: If transaction fails.
    """
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Transaction failed, rolled back: {e}")
        raise


def close_db(e: Exception | None = None) -> None:
    """Close the database connection at end of request.

    Args:
        e: Optional exception that triggered the teardown.
    """
    db = g.pop("db", None)
    if db is not None:
        try:
            db.close()
        except Exception as ex:
            current_app.logger.error(f"Error closing database connection: {ex}")


def init_app(app: Flask) -> None:
    """Register database teardown handler with Flask app.

    Args:
        app: The Flask application instance.
    """
    app.teardown_appcontext(close_db)
