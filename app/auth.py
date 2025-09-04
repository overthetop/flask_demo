"""Authentication helpers.

Thin wrappers around Werkzeug's password hashing utilities and a simple
`login_required` decorator for protecting views. Session use is minimal and
kept in one place for clarity.
"""

import functools

from flask import current_app, flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password):
    """Hash a plaintext password using a secure algorithm."""
    current_app.logger.info("Hashing password for user")
    return generate_password_hash(password)


def verify_password(stored_password, provided_password):
    """Verify a stored password hash against user input."""
    result = check_password_hash(stored_password, provided_password)
    # Note: We don't log the result here for security reasons
    return result


def login_user(user_id):
    """Log in a user by setting the `session['user_id']`."""
    session.clear()
    session["user_id"] = user_id
    current_app.logger.info(f"User {user_id} logged in")


def logout_user():
    """Log out the current user and clear the session."""
    user_id = session.get("user_id")
    session.clear()
    current_app.logger.info(f"User {user_id} logged out")


def login_required(view):
    """Decorator to require login for a view.

    If the user is not authenticated, flashes a message and redirects to
    the login page. Otherwise, calls the wrapped view.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            current_app.logger.warning("Unauthorized access attempt to protected view")
            flash("You need to be logged in to view this page.")
            return redirect(url_for("main.login"))
        return view(**kwargs)

    return wrapped_view
