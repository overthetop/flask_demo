"""Authentication helpers for user session management."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import flash, g, redirect, session, url_for


def login_user(user_id: int) -> None:
    """Store user_id in session after clearing any existing session data.

    Args:
        user_id: The database ID of the user to log in.
    """
    session.clear()
    session["user_id"] = user_id


def logout_user() -> None:
    """Clear the current session, logging out the user."""
    session.clear()


def login_required(view: Callable) -> Callable:
    """Decorator to require authentication for a view.

    Redirects to login page if user is not authenticated.
    Use with: @login_required

    Args:
        view: The view function to protect.

    Returns:
        Wrapped view function that checks authentication.
    """

    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if g.user is None:
            flash("You need to be logged in to view this page.")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapper
