"""Authentication helpers."""

from functools import wraps

from flask import flash, g, redirect, session, url_for


def login_user(user_id):
    """Store user_id in session."""
    session.clear()
    session["user_id"] = user_id


def logout_user():
    """Clear the session."""
    session.clear()


def login_required(view):
    """Decorator to require authentication."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if g.user is None:
            flash("You need to be logged in to view this page.")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapper
