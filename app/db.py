import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app, g
import click
from flask.cli import with_appcontext


def get_db():
    """Get database connection from Flask context or create a new one."""
    if "db" not in g:
        database_url = current_app.config["DATABASE_URL"]
        current_app.logger.debug(f"Connecting to database: {database_url}")
        if database_url.startswith("postgresql://"):
            g.db = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        else:
            g.db = sqlite3.connect(database_url, detect_types=sqlite3.PARSE_DECLTYPES)
            g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection."""
    db = g.pop("db", None)
    if db is not None:
        current_app.logger.debug("Closing database connection")
        db.close()


def init_db():
    """Initialize database with required tables."""
    db = get_db()
    database_url = current_app.config["DATABASE_URL"]
    current_app.logger.info("Initializing database")

    if database_url.startswith("postgresql://"):
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
    else:
        # SQLite setup
        # Create users table
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create posts table
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        db.commit()
    current_app.logger.info("Database initialized")


def init_app(app):
    """Register database functions with Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
