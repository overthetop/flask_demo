# Flask Showcase Application

An educational Flask application demonstrating modern web development patterns with minimal dependencies. Learn Flask basics through clean, well-documented code.

## Table of Contents

- [Technologies](#technologies)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Features](#features)
- [Configuration](#configuration)
- [Development](#development)
- [API Endpoints](#api-endpoints)
- [Architecture](#architecture)
- [Key Concepts](#key-concepts)
- [Troubleshooting](#troubleshooting)
- [Security](#security)

---

## Technologies

This application demonstrates:
- **Flask 3** - Modern Python web framework
- **PostgreSQL** - Relational database with raw SQL via psycopg 3
- **Jinja2** - Template engine for dynamic HTML
- **Waitress** - Production WSGI server
- **Werkzeug** - Password hashing and security
- **Ruff** - Fast Python linter and formatter

**Patterns**: Application factory, blueprints, session-based authentication, request context

---

## Quick Start

### 1. Set Up Python Environment

**Create and activate virtual environment:**

```bash
# macOS/Linux
python3 -m venv venv && source venv/bin/activate

# Windows
python -m venv venv && venv\Scripts\activate

# Or use the convenience script (macOS/Linux)
./activate.sh
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### 2. Start PostgreSQL Database

**Using Docker (recommended):**
```bash
docker compose up -d
```

The database schema (`init-db.sql`) is applied automatically on first start.

### 3. Configure Environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_showcase
SECRET_KEY=dev-change-me
FLASK_DEBUG=1
```

**Note**: For production, generate a secure key with `openssl rand -hex 32`

### 4. Run the Application

**Development server** (with auto-reload):
```bash
python app.py
```
Open http://localhost:5000

**Production server** (Waitress):
```bash
python wsgi.py
```
Open http://localhost:8000

---

## Project Structure

```
├── app.py              # App factory + dev entrypoint
├── wsgi.py             # Production entrypoint (Waitress)
├── config.py           # Environment-driven configuration
├── db.py               # Database connection helpers
├── auth.py             # Authentication helpers
├── routes.py           # All routes and views (blueprint)
├── errors.py           # Error handlers (404, 500)
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, images, JavaScript
├── init-db.sql         # PostgreSQL schema
├── docker-compose.yml  # Dev database setup
├── requirements.txt    # Python dependencies
└── pyproject.toml      # Ruff configuration
```

**Key Files:**
- **app.py** - Creates Flask app, registers blueprints
- **routes.py** - All application routes and views
- **auth.py** - `login_required` decorator, session helpers
- **db.py** - Request-scoped database connections
- **config.py** - Environment variables and settings

---

## Features

- User registration and authentication
- Session management with secure cookies
- Post creation and viewing
- Protected routes with `@login_required`
- PostgreSQL integration with parameterized queries
- Health check endpoint for monitoring
- Structured logging
- Production-ready WSGI server

---

## Configuration

Configure the application using environment variables in a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/flask_showcase` |
| `SECRET_KEY` | Secret for session signing | Random (regenerates on restart) |
| `FLASK_DEBUG` | Enable debug mode | `0` (disabled) |

**Important Notes:**
- The default `DATABASE_URL` matches the Docker Compose service
- Omitting `SECRET_KEY` generates a random one (dev only - sessions invalidate on restart)
- **Always set `SECRET_KEY` explicitly in production**

**Generate a secure secret key:**
```bash
openssl rand -hex 32
```

---

## Development

### Code Quality Tools

**Ruff** is included in `requirements.txt` for linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

**Configuration** (in `pyproject.toml`):
- Line length: 88 characters
- Target: Python 3.12
- Rules: E (pycodestyle), F (pyflakes), I (isort), B (bugbear), UP (pyupgrade), C4 (comprehensions)

### Database Commands

**Docker Compose:**
```bash
# Start database
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop database
docker compose down

# Stop and remove data
docker compose down -v
```

**Manual schema initialization** (if not using Docker Compose):
```bash
# Using psql
psql postgresql://postgres:postgres@localhost:5432/flask_showcase -f init-db.sql

# Or with Docker
docker compose exec -T db psql -U postgres -d flask_showcase < init-db.sql
```

### Adding New Routes

**Basic route** in `routes.py`:
```python
@main.route("/your-path")
def your_view():
    return render_template("your_template.html")
```

**Protected route** (requires authentication):
```python
@main.route("/protected")
@login_required
def protected_view():
    # g.user is guaranteed to exist here
    return render_template("protected.html", user=g.user)
```

---

## API Endpoints

### Web Routes

| Route | Method | Description | Auth Required |
|-------|--------|-------------|---------------|
| `/` | GET | Home page with posts | No |
| `/register` | GET/POST | User registration | No |
| `/login` | GET/POST | User login | No |
| `/logout` | GET | User logout | No |
| `/profile` | GET | User profile page | Yes |
| `/posts` | GET | List all posts | No |
| `/posts/create` | GET/POST | Create new post | Yes |
| `/posts/<post_id>` | GET | View single post | No |
| `/health` | GET | Health check endpoint | No |

### Health Check

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy"
}
```

---

## Architecture

### High-Level Overview

```mermaid
flowchart TD
  %% Nodes
  A[Client/Browser]
  J[Dev Server app.py]
  K[Waitress wsgi.py]
  B[Flask App]
  C[routes.py main blueprint]
  D[auth.py helpers]
  E["db.py (psycopg)"]
  F[errors.py handlers]
  G[templates/ Jinja2]
  H[static/ files]
  I[(PostgreSQL)]

  %% Edges
  A --> J
  A --> K
  J --> B
  K --> B

  subgraph Flask Application
    B --> C
    C --> D
    C --> E
    C --> F
    B --> G
    B --> H
  end

  E --> I
```

### Request Flow: Login

```mermaid
sequenceDiagram
  participant B as Browser
  participant F as Flask App
  participant R as Routes (Blueprint)
  participant A as Auth Helpers
  participant D as DB (psycopg)
  participant T as Templates

  B->>F: POST /login (username, password)
  activate F
  F->>R: before_app_request
  R->>D: Load g.user from session
  D-->>R: user row or None
  R-->>F: g.user set

  F->>R: handle /login
  R->>D: SELECT user WHERE username
  D-->>R: user row
  R->>R: check_password_hash(hash, password)
  Note over R: Using werkzeug security
  alt valid credentials
    R->>F: login_user -> session['user_id']
    F->>T: render flash + redirect
    T-->>B: 302 -> /
  else invalid
    R-->>B: 200 form with error message
  end
  deactivate F
```

### Request Flow: Create Post

```mermaid
sequenceDiagram
  participant B as Browser
  participant F as Flask App
  participant R as Routes (Blueprint)
  participant A as Auth Helpers
  participant D as DB (psycopg)
  participant T as Templates

  Note over B,F: Access form
  B->>F: GET /posts/create
  activate F
  F->>R: before_app_request
  R->>D: Load g.user from session
  D-->>R: user row or None
  R-->>F: g.user set
  R->>A: login_required check
  alt not authenticated
    R-->>B: 302 redirect to /login
  else authenticated
    F->>T: render create form
    T-->>B: 200 form
  end
  deactivate F

  Note over B,F: Submit new post
  B->>F: POST /posts/create (title, content)
  activate F
  F->>R: validate title
  alt valid
    R->>D: INSERT INTO posts (title, content, user_id)
    D-->>R: commit ok
    R-->>B: 302 redirect to /posts (flash message)
  else invalid
    R->>T: re-render form with error
    T-->>B: 200 form with error
  end
  deactivate F
```

---

## Key Concepts

### Request Context (flask.g)

Per-request storage that's cleared after each request:
- **`g.user`** - Current user loaded by `@main.before_app_request`
- **`g.db`** - Database connection managed by `get_db()`

### Session Management

- Session stores only `user_id` (minimal data)
- Full user data loaded into `g.user` on each request
- Sessions are signed with `SECRET_KEY` for security

### Database Pattern

- One connection per request via `flask.g`
- Returns rows as dictionaries (`dict_row` factory)
- Automatic cleanup via `teardown_appcontext`
- Parameterized queries prevent SQL injection

**Example database usage:**
```python
from db import get_db

db = get_db()
with db.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
```

---

## Troubleshooting

### Database Connection Errors

**Check if PostgreSQL is running:**
```bash
docker compose ps
```

**Verify configuration:**
- Check `DATABASE_URL` in `.env` file
- Ensure database exists: `flask_showcase`
- Verify credentials match Docker Compose settings

### Environment Variables Not Loading

- Ensure `.env` file exists in project root (same directory as `app.py`)
- Check file permissions are readable
- Restart the application after changing `.env`

### psycopg Installation Issues (Windows)

If you encounter build errors:

```bash
# Update pip
python -m pip install --upgrade pip

# Install binary package
pip install psycopg[binary]
```

### Port Already in Use

If port 5000 or 8000 is already in use:

```bash
# Find process using port
# macOS/Linux
lsof -i :5000

# Windows
netstat -ano | findstr :5000

# Kill the process or use a different port
python app.py  # Set FLASK_RUN_PORT=5001 in .env
```

---

## Security

### Best Practices Implemented

- **Password hashing** - Werkzeug's `generate_password_hash()` with salt
- **SQL injection prevention** - Parameterized queries throughout
- **Session security** - Signed cookies with `SECRET_KEY`
- **Secrets management** - `.env` file (excluded from git)

### Security Checklist

- [ ] Never commit `.env` file (already in `.gitignore`)
- [ ] Generate strong `SECRET_KEY` for production: `openssl rand -hex 32`
- [ ] Use production WSGI server (Waitress/Gunicorn), not Flask dev server
- [ ] Enable HTTPS in production
- [ ] Keep dependencies updated: `pip list --outdated`
- [ ] Review database connection strings (no passwords in code)

### Production Deployment

**Do not use Flask's development server in production:**
```bash
# Bad (dev only)
python app.py

# Good (production)
python wsgi.py
```

The development server is not designed for production workloads. Use Waitress (included) or Gunicorn.

---

## Next Steps

**For learners:**
- Read `TUTOR.md` for detailed Flask concepts
- Experiment with adding new routes
- Try adding your own templates
- Explore the database schema in `init-db.sql`

**For production:**
- Add CSRF protection (Flask-WTF)
- Implement input validation
- Add connection pooling (psycopg_pool)
- Set up proper logging (file handlers)
- Create comprehensive tests
- Add rate limiting (Flask-Limiter)

---

**Questions?** Check out the [Flask documentation](https://flask.palletsprojects.com/) or review the code comments for detailed explanations.
