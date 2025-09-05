"""Application routes and views.

Routes are grouped under the `main` blueprint and demonstrate:
- Server-rendered pages (index, posts, auth forms)
- Simple REST endpoints for posts
- Request lifecycle hooks to load the current user

All SQL is written explicitly using `psycopg` to keep dependencies light.
"""

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

from app.auth import (
    hash_password,
    login_required,
    login_user,
    logout_user,
    verify_password,
)
from app.db import get_db

main = Blueprint("main", __name__)


@main.before_app_request
def load_logged_in_user():
    """Load the current user into `g.user` for each request.

    This runs before every request so templates and views can rely on
    `g.user` being either a user row (dict-like) or `None`.
    """
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,),
            )
            g.user = cursor.fetchone()
        current_app.logger.debug(f"Loaded user {user_id}")


@main.route("/")
def index():
    """Render the home page with the most recent posts."""
    current_app.logger.info("Accessing home page")
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
    current_app.logger.debug(f"Fetched {len(posts)} posts for home page")
    return render_template("index.html", posts=posts)


@main.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    On POST, performs minimal validation and creates the user with a hashed
    password. On success, redirects to the login page.
    """
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        error = None
        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."

        db = get_db()
        with db.cursor() as cursor:
            if error is None:
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s OR email = %s",
                    (username, email),
                )
                if cursor.fetchone() is not None:
                    error = "User with this username or email already exists."

            if error is None:
                current_app.logger.info(f"Registering new user: {username}")
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) "
                    "VALUES (%s, %s, %s)",
                    (username, email, hash_password(password)),
                )
                db.commit()
                flash("Registration successful! Please log in.")
                current_app.logger.info(f"User {username} registered successfully")
                return redirect(url_for("main.login"))

        if error is not None:
            flash(error)
            current_app.logger.warning(f"Registration failed: {error}")

    return render_template("auth/register.html")


@main.route("/login", methods=("GET", "POST"))
def login():
    """Authenticate a user and start a session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        with db.cursor() as cursor:
            error = None

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user is None or not verify_password(user["password_hash"], password):
                error = "Incorrect username or password."

            if error is None:
                login_user(user["id"])
                flash("Logged in successfully!")
                current_app.logger.info(f"User {username} logged in successfully")
                return redirect(url_for("main.index"))

            flash(error)
            current_app.logger.warning(f"Login failed for {username}: {error}")

    return render_template("auth/login.html")


@main.route("/logout")
def logout():
    """Log out the current user."""
    logout_user()
    flash("You have been logged out.")
    current_app.logger.info("User logged out")
    return redirect(url_for("main.index"))


@main.route("/profile")
@login_required
def profile():
    """User profile page (requires login)."""
    current_app.logger.debug(f"Accessing profile for user {g.user['id']}")
    return render_template("auth/profile.html")


@main.route("/posts")
def posts():
    """List all posts (server-rendered)."""
    current_app.logger.info("Accessing posts page")
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
    current_app.logger.debug(f"Fetched {len(posts)} posts")
    return render_template("posts/index.html", posts=posts)


@main.route("/posts/create", methods=("GET", "POST"))
@login_required
def create_post():
    """Create a new post (requires login)."""
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
            current_app.logger.warning(f"Post creation failed: {error}")
        else:
            current_app.logger.info(f"Creating new post: {title}")
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)",
                    (title, content, g.user["id"]),
                )
                db.commit()
            flash("Post created successfully!")
            current_app.logger.info(f"Post '{title}' created successfully")
            return redirect(url_for("main.posts"))

    return render_template("posts/create.html")


@main.route("/posts/<int:id>")
def post_detail(id):
    """Display a single post by id."""
    current_app.logger.debug(f"Accessing post detail for post {id}")
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
        """,
            (id,),
        )
        post = cursor.fetchone()

    if post is None:
        current_app.logger.warning(f"Post {id} not found")
        flash("Post not found.")
        return redirect(url_for("main.posts"))

    current_app.logger.debug(f"Displaying post {id}")
    return render_template("posts/detail.html", post=post)


@main.route("/api/posts")
def api_posts():
    """Return all posts as JSON for API consumers."""
    current_app.logger.info("Accessing API posts endpoint")
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

    # Convert to list of dictionaries
    posts_list = [dict(post) for post in posts]
    current_app.logger.debug(f"Returning {len(posts_list)} posts via API")
    return {"posts": posts_list}


@main.route("/api/posts/<int:id>")
def api_post_detail(id):
    """Return a single post as JSON or 404 if missing."""
    current_app.logger.debug(f"Accessing API post detail for post {id}")
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
        """,
            (id,),
        )
        post = cursor.fetchone()

    if post is None:
        current_app.logger.warning(f"Post {id} not found via API")
        return {"error": "Post not found"}, 404

    current_app.logger.debug(f"Returning post {id} via API")
    return dict(post)


@main.route("/health")
def health_check():
    """Lightweight health check for readiness probes."""
    current_app.logger.debug("Health check accessed")
    return {"status": "healthy"}, 200
