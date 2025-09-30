# Flask Showcase Application

An educational Flask application demonstrating common patterns and best practices with a minimal dependency set: raw SQL via psycopg, app factory + blueprints, simple auth, templates, JSON APIs, and production serving via Waitress.

## Quickstart

1) Create and activate a venv
- macOS/Linux: `python3 -m venv venv && source venv/bin/activate`
- Windows (cmd): `python -m venv venv && venv\Scripts\activate`
- Alternatively: `./activate.sh` (macOS/Linux)

2) Install dependencies
- `pip install -r requirements.txt` (includes Ruff linter/formatter)

3) Start a local PostgreSQL (recommended)
- `docker compose up -d`

4) Configure environment (`.env` in project root)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_showcase
SECRET_KEY=dev-change-me
# Flask 3: use FLASK_DEBUG for dev
FLASK_DEBUG=1
```

5) Initialize the database schema
- Using Docker Compose: schema is applied automatically on first container start via `docker-entrypoint-initdb.d/init-db.sql`.
- Otherwise, run manually:
  - `docker compose exec -T db psql -U postgres -d flask_showcase < init-db.sql`
  - or `psql postgresql://postgres:postgres@localhost:5432/flask_showcase -f init-db.sql`
  - Windows (psql installed): `psql -h localhost -p 5432 -U postgres -d flask_showcase -f init-db.sql`

6) Run the app
- Dev server: `python app.py` → http://localhost:5000
- Waitress: `python wsgi.py` → http://localhost:8000

Linting and formatting (Ruff is included in requirements.txt):
- Lint: `ruff check .` (auto-fix: `ruff check . --fix`)
- Format: `ruff format .`

## Project Structure

```
app.py              # app factory + development entrypoint
wsgi.py             # production entrypoint (Waitress)
config.py           # env-driven configuration
db.py               # psycopg connection helpers
auth.py             # hashing helpers + login_required
routes.py           # views + API endpoints (blueprint)
errors.py           # error handlers
templates/          # Jinja templates
static/             # CSS, images, JS
init-db.sql         # database schema
docker-compose.yml  # dev database
requirements.txt    # pinned deps (includes Ruff)
pyproject.toml      # Ruff configuration
```

## Architecture

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

## Features

- User authentication (register, login, logout)
- Post creation and viewing
- Session management
- PostgreSQL database integration
- Structured logging
- Health check endpoint

## Request Flow (Login)

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
  R->>A: verify_password(hash, password)
  A-->>R: result (true/false)
  alt valid credentials
    R->>F: login_user -> session['user_id']
    F->>T: render flash + redirect
    T-->>B: 302 -> /
  else invalid
    R-->>B: 200 form with error message
  end
  deactivate F
```

## Request Flow (Create Post)

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

- Flask blueprints for route organization
- PostgreSQL with raw SQL queries via psycopg 3
- Jinja2 templating
- Session-based authentication
- Structured logging
- Production-ready with Waitress WSGI server

## API Endpoints

- `GET /health` — Health check

## Configuration

Environment variables (set in `.env` file):

- `DATABASE_URL` — PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/flask_showcase`)
- `SECRET_KEY` — Secret for session signing (default: random, regenerated on restart)
- `FLASK_DEBUG` — Enable debug mode (set to `1` or `true` for development)

**Notes:**
- Default `DATABASE_URL` matches the docker-compose service
- Omitting `SECRET_KEY` generates a random one (fine for dev, but sessions invalidate on restart)
- In production, always set `SECRET_KEY` explicitly

## Key Concepts

**Request Context (flask.g)**
- Stores per-request data (cleared after each request)
- `g.user` - Current user loaded by `@main.before_app_request`
- `g.db` - Database connection managed by `get_db()`

**Session Management**
- Session stores only `user_id`
- User data loaded into `g.user` on each request
- Signed with `SECRET_KEY`

**Database Pattern**
- One connection per request via `flask.g`
- Returns rows as dictionaries (`dict_row` factory)
- Automatic cleanup via `teardown_appcontext`

## Docker Compose Commands

```bash
docker compose up -d          # Start PostgreSQL
docker compose ps             # Check status
docker compose down           # Stop containers
docker compose down -v        # Stop and remove volumes
```

Schema is auto-applied from `init-db.sql` on first start.

## Troubleshooting

**Database connection errors:**
- Check PostgreSQL is running: `docker compose ps`
- Verify `DATABASE_URL` in `.env`

**Environment variables not loading:**
- Ensure `.env` file exists in project root
- Check file permissions

**psycopg installation issues (Windows):**
- Update pip: `python -m pip install --upgrade pip`
- Use binary package: `pip install psycopg[binary]`

## Security

- Never commit `.env` file (already in `.gitignore`)
- Generate strong `SECRET_KEY`: `openssl rand -hex 32`
- Use Waitress or Gunicorn in production (not Flask dev server)
- Passwords are hashed with Werkzeug's `generate_password_hash()`
- SQL injection prevented via parameterized queries

## Development Tools

**Ruff** (linter & formatter, included in `requirements.txt`):
```bash
ruff check .        # Lint
ruff check . --fix  # Auto-fix
ruff format .       # Format
```

Configuration in `pyproject.toml`:
- Line length: 88
- Target: Python 3.12
- Rules: E (pycodestyle), F (pyflakes), I (isort), B (bugbear), UP (pyupgrade), C4 (comprehensions)


## Adding Routes

1. Define function in `routes.py`:
```python
@main.route("/your-path")
def your_view():
    return render_template("your_template.html")
```

2. Protect with authentication:
```python
@main.route("/protected")
@login_required
def protected_view():
    # g.user is guaranteed to exist here
    return render_template("protected.html")
```

## Code Overview

**app.py** - Application factory and dev server
- Creates Flask app instance
- Configures simple structured logging
- Registers blueprint, error handlers, and database teardown

**config.py** - Environment configuration
- `SECRET_KEY` - Session signing (random fallback for dev)
- `DATABASE_URL` - PostgreSQL connection string

**db.py** - Database helpers
- `get_db()` - Request-scoped connection with dict_row factory
- `close_db()` - Closes connection on request teardown

**auth.py** - Authentication
- `login_user(user_id)` - Store user in session
- `logout_user()` - Clear session
- `login_required` - Decorator for protected routes

**routes.py** - Blueprint with all routes
- `/` - Home page with posts
- `/register`, `/login`, `/logout` - Auth flows
- `/profile` - User profile (requires login)
- `/posts`, `/posts/create`, `/posts/<post_id>` - Post management
- `/health` - Health check endpoint

**errors.py** - Error handlers
- 404 and 500 pages with logging

