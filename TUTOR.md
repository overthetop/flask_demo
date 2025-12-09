# Flask Showcase Tutorial

Learn Flask by exploring this application step by step.

## Table of Contents
1. [What is Flask?](#what-is-flask)
2. [Project Structure](#project-structure)
3. [Key Flask Concepts](#key-flask-concepts)
4. [Database Integration](#database-integration)
5. [Authentication System](#authentication-system)
6. [Templates](#templates)
7. [Running the Application](#running-the-application)
8. [Learning Exercises](#learning-exercises)

## What is Flask?

Flask is a lightweight web framework for Python. It's called a microframework because it doesn't require particular tools or libraries.

**Why Flask for beginners:**
1. Simple and easy to understand
2. Flexible - doesn't force a specific structure
3. Excellent documentation
4. Widely used in industry

## Project Structure

```
├── app.py          # App factory + dev server
├── wsgi.py         # Production server (Waitress)
├── config.py       # Configuration settings
├── db.py           # Database connection
├── auth.py         # Authentication helpers
├── routes.py       # All routes (blueprint)
├── errors.py       # Error handlers (404, 500)
├── templates/      # HTML templates
├── static/         # CSS, images, JS
└── init-db.sql     # Database schema
```

## Key Flask Concepts

### 1. Application Factory Pattern

Instead of creating a Flask app globally, we use a factory function:

```python
# app.py
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main)
    register_error_handlers(app)
    init_app(app)

    return app
```

**Benefits:**
- Makes testing easier
- Allows multiple app instances
- Better organization

### 2. Blueprints

Blueprints organize routes into modules. This project uses one blueprint (`main`) in `routes.py`:

```python
# routes.py
from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html", posts=posts)
```

Registered in `app.py` via `app.register_blueprint(main)`.

### 3. Request Hooks

Run code before every request:

```python
@main.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            g.user = cursor.fetchone()
```

This loads the current user into `g.user` for every request.

### 4. Template Inheritance

Templates extend a base layout:

```html
<!-- templates/base.html -->
<html>
  <head><title>{% block title %}{% endblock %}</title></head>
  <body>{% block content %}{% endblock %}</body>
</html>
```

Child templates:

```html
{% extends "base.html" %}
{% block title %}Home{% endblock %}
{% block content %}
  <h1>Welcome</h1>
{% endblock %}
```

## Database Integration

### Connection Pattern

The `get_db()` function in `db.py` creates one connection per request:

```python
def get_db():
    if "db" not in g:
        g.db = psycopg.connect(
            current_app.config["DATABASE_URL"],
            row_factory=dict_row,
        )
    return g.db
```

**Key points:**
- Connection stored in `flask.g` (request-local storage)
- `dict_row` returns rows as dictionaries
- Connection closed automatically after each request

### Using the Database

```python
db = get_db()
with db.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
```

Always use parameterized queries (`%s`) to prevent SQL injection.

## Authentication System

### Password Hashing

Passwords are hashed using Werkzeug (in `routes.py`):

```python
from werkzeug.security import generate_password_hash, check_password_hash

# When registering
password_hash = generate_password_hash(password)

# When logging in
if check_password_hash(user["password_hash"], password):
    # Password is correct
```

### Session Management

`auth.py` provides simple helpers:

```python
def login_user(user_id):
    session.clear()
    session["user_id"] = user_id

def logout_user():
    session.clear()
```

### Login Required Decorator

Protect routes that need authentication:

```python
def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if g.user is None:
            flash("You need to be logged in.")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapper
```

Usage:

```python
@main.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html")
```

## Templates

### Passing Data to Templates

```python
# In routes.py
return render_template('index.html', posts=posts)

# In templates/index.html
{% for post in posts %}
  <h2>{{ post.title }}</h2>
  <p>{{ post.content }}</p>
{% endfor %}
```

### Flash Messages

Show one-time messages to users:

```python
# In routes.py
flash('Registration successful!')

# In templates
{% with messages = get_flashed_messages() %}
  {% for message in messages %}
    <div class="alert">{{ message }}</div>
  {% endfor %}
{% endwith %}
```

### Styling

Custom CSS is in `static/style.css`. The `url_for()` function generates URLs:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

## Running the Application

### Development

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start database
docker compose up -d

# 4. Create .env file
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_showcase
SECRET_KEY=dev-secret-key
FLASK_DEBUG=1

# 5. Run
python app.py
```

Open http://localhost:5000

### Production

```bash
python wsgi.py
```

Open http://localhost:8000

## Learning Exercises

Try these to learn more:

1. **Add a route** - Create a new page in `routes.py` using `@main.route`
2. **Modify a template** - Change `templates/index.html`
3. **Add form validation** - Check input length before saving to database
4. **Add a new field** - Add a "bio" field to user profiles
5. **Add pagination** - Limit posts per page with LIMIT/OFFSET

## Common Patterns

### Handling Forms

```python
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method != 'POST':
        return render_template('auth/register.html')

    username = request.form['username']
    # ... validation and processing
```

### Error Handling

```python
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
```

## Next Steps

1. **Flask Documentation** - https://flask.palletsprojects.com/
2. **Flask Extensions** - SQLAlchemy for ORM, Flask-WTF for forms
3. **Testing** - Write tests with pytest
4. **Security** - Add CSRF protection, input validation

## Code References

Main files and their key functions:

| File | Key Functions |
|------|---------------|
| `app.py` | `create_app()`, `setup_logging()` |
| `routes.py` | `index()`, `register()`, `login()`, `logout()`, `profile()`, `posts()`, `create_post()`, `post_detail()` |
| `db.py` | `get_db()`, `close_db()`, `init_app()` |
| `auth.py` | `login_user()`, `logout_user()`, `login_required()` |
| `errors.py` | `register_error_handlers()` |
| `config.py` | `Config` class |

## Linting

This project uses Ruff for code quality:

```bash
ruff check .           # Check for issues
ruff check . --fix     # Auto-fix issues
ruff format .          # Format code
```
