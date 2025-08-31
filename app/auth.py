from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, current_app
import functools
from flask import flash, redirect, url_for


def hash_password(password):
    """Hash a password for storing."""
    current_app.logger.info("Hashing password for user")
    return generate_password_hash(password)


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user."""
    result = check_password_hash(stored_password, provided_password)
    # Note: We don't log the result here for security reasons
    return result


def login_user(user_id):
    """Log in a user by setting the session."""
    session.clear()
    session["user_id"] = user_id
    current_app.logger.info(f"User {user_id} logged in")


def logout_user():
    """Log out the current user."""
    user_id = session.get("user_id")
    session.clear()
    current_app.logger.info(f"User {user_id} logged out")


def login_required(view):
    """Decorator to require login for a view."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            current_app.logger.warning("Unauthorized access attempt to protected view")
            flash("You need to be logged in to view this page.")
            return redirect(url_for("main.login"))
        return view(**kwargs)

    return wrapped_view
