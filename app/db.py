"""Database helpers and CLI integration.

This module manages a single psycopg2 connection per request context via
`flask.g`, exposes a simple `init-db` Click command, and provides helpers to
open/close the connection gracefully.
"""

import click
import psycopg2
from flask import current_app, g
from flask.cli import with_appcontext
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


def init_db():
    """Create required tables if they do not exist.

    This function is idempotent and safe to run multiple times.
    """
    db = get_db()
    current_app.logger.info("Initializing database")

    # PostgreSQL setup
    cursor = db.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create posts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    db.commit()
    cursor.close()
    current_app.logger.info("Database initialized")


def init_app(app):
    """Register teardown and CLI commands on the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """CLI: create required tables for the application."""
    init_db()
    click.echo("Initialized the database.")
