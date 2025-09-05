"""Authentication helpers.

Thin wrappers around Werkzeug's password hashing utilities and a simple
`login_required` decorator for protecting views. Session use is minimal and
kept in one place for clarity.
"""

from functools import wraps

from flask import current_app, flash, g, redirect, session, url_for
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


def _redirect_to_login():
    """Log, inform the user, and redirect to the login page."""
    current_app.logger.warning("Unauthorized access attempt to protected view")
    flash("You need to be logged in to view this page.")
    return redirect(url_for("main.login"))


def is_authenticated() -> bool:
    """Return True if the current request has an authenticated user.

    Prefer `g.user` set by the request hook; fall back to the session key.
    """
    if getattr(g, "user", None):
        return True
    return "user_id" in session


def login_required(view):
    """Require login for a view in a straightforward, readable way."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return _redirect_to_login()
        return view(*args, **kwargs)

    return wrapper
