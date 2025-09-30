"""Application routes and views."""

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from auth import login_required, login_user, logout_user
from db import get_db

main = Blueprint("main", __name__)


@main.before_app_request
def load_logged_in_user():
    """Load current user into g.user for each request."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            g.user = cursor.fetchone()


@main.route("/")
def index():
    """Render home page with recent posts."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.id, p.title, p.content, p.created_at, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            """
        )
        posts = cursor.fetchall()
    return render_template("index.html", posts=posts)


@main.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user."""
    if request.method != "POST":
        return render_template("auth/register.html")

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    if not username or not email or not password:
        flash("All fields are required.")
        return render_template("auth/register.html")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cursor.fetchone():
            flash("Username or email already exists.")
            return render_template("auth/register.html")

        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, generate_password_hash(password)),
        )
        db.commit()

    flash("Registration successful! Please log in.")
    return redirect(url_for("main.login"))


@main.route("/login", methods=("GET", "POST"))
def login():
    """Authenticate user and start session."""
    if request.method != "POST":
        return render_template("auth/login.html")

    username = request.form["username"]
    password = request.form["password"]

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Incorrect username or password.")
        current_app.logger.warning(f"Failed login attempt for: {username}")
        return render_template("auth/login.html")

    login_user(user["id"])
    flash("Logged in successfully!")
    return redirect(url_for("main.index"))


@main.route("/logout")
def logout():
    """Log out current user."""
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@main.route("/profile")
@login_required
def profile():
    """User profile page."""
    return render_template("auth/profile.html")


@main.route("/posts")
def posts():
    """List all posts."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.id, p.title, p.content, p.created_at, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            """
        )
        posts = cursor.fetchall()
    return render_template("posts/index.html", posts=posts)


@main.route("/posts/create", methods=("GET", "POST"))
@login_required
def create_post():
    """Create a new post."""
    if request.method != "POST":
        return render_template("posts/create.html")

    title = request.form["title"]
    content = request.form["content"]

    if not title:
        flash("Title is required.")
        return render_template("posts/create.html")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)",
            (title, content, g.user["id"]),
        )
        db.commit()

    flash("Post created successfully!")
    return redirect(url_for("main.posts"))


@main.route("/posts/<int:post_id>")
def post_detail(post_id):
    """Display a single post."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.id, p.title, p.content, p.created_at, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
            """,
            (post_id,),
        )
        post = cursor.fetchone()

    if not post:
        flash("Post not found.")
        current_app.logger.warning(f"Post {post_id} not found")
        return redirect(url_for("main.posts"))

    return render_template("posts/detail.html", post=post)


@main.route("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}, 200
