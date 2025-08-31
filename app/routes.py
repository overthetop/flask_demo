from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g,
    current_app,
)
from app.db import get_db
from app.auth import (
    hash_password,
    verify_password,
    login_user,
    logout_user,
    login_required,
)

main = Blueprint("main", __name__)


@main.before_app_request
def load_logged_in_user():
    """Load logged in user data before each request."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
        )
        g.user = cursor.fetchone()
        cursor.close()
        current_app.logger.debug(f"Loaded user {user_id}")


@main.route("/")
def index():
    """Home page showing recent posts."""
    current_app.logger.info("Accessing home page")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        """
    )
    posts = cursor.fetchall()
    cursor.close()
    current_app.logger.debug(f"Fetched {len(posts)} posts for home page")
    return render_template("index.html", posts=posts)


@main.route("/register", methods=("GET", "POST"))
def register():
    """User registration page."""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        else:
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
            cursor.close()
            flash("Registration successful! Please log in.")
            current_app.logger.info(f"User {username} registered successfully")
            return redirect(url_for("main.login"))

        flash(error)
        current_app.logger.warning(f"Registration failed: {error}")
        cursor.close()

    return render_template("auth/register.html")


@main.route("/login", methods=("GET", "POST"))
def login():
    """User login page."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        error = None

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user is None:
            error = "Incorrect username or password."
        elif not verify_password(user["password_hash"], password):
            error = "Incorrect username or password."

        if error is None:
            login_user(user["id"])
            flash("Logged in successfully!")
            current_app.logger.info(f"User {username} logged in successfully")
            return redirect(url_for("main.index"))

        flash(error)
        current_app.logger.warning(f"Login failed for {username}: {error}")
        cursor.close()

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
    """Display all posts."""
    current_app.logger.info("Accessing posts page")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        """
    )
    posts = cursor.fetchall()
    cursor.close()
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
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)",
                (title, content, g.user["id"]),
            )
            db.commit()
            cursor.close()
            flash("Post created successfully!")
            current_app.logger.info(f"Post '{title}' created successfully")
            return redirect(url_for("main.posts"))

    return render_template("posts/create.html")


@main.route("/posts/<int:id>")
def post_detail(id):
    """Display a single post."""
    current_app.logger.debug(f"Accessing post detail for post {id}")
    db = get_db()
    cursor = db.cursor()
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
    cursor.close()

    if post is None:
        current_app.logger.warning(f"Post {id} not found")
        flash("Post not found.")
        return redirect(url_for("main.posts"))

    current_app.logger.debug(f"Displaying post {id}")
    return render_template("posts/detail.html", post=post)


@main.route("/api/posts")
def api_posts():
    """API endpoint to get all posts as JSON."""
    current_app.logger.info("Accessing API posts endpoint")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        """
    )
    posts = cursor.fetchall()
    cursor.close()

    # Convert to list of dictionaries
    posts_list = [dict(post) for post in posts]
    current_app.logger.debug(f"Returning {len(posts_list)} posts via API")
    return {"posts": posts_list}


@main.route("/api/posts/<int:id>")
def api_post_detail(id):
    """API endpoint to get a single post as JSON."""
    current_app.logger.debug(f"Accessing API post detail for post {id}")
    db = get_db()
    cursor = db.cursor()
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
    cursor.close()

    if post is None:
        current_app.logger.warning(f"Post {id} not found via API")
        return {"error": "Post not found"}, 404

    current_app.logger.debug(f"Returning post {id} via API")
    return dict(post)


@main.route("/health")
def health_check():
    """Health check endpoint."""
    current_app.logger.debug("Health check accessed")
    return {"status": "healthy"}, 200
