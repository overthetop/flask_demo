# Flask Showcase Application

An educational Flask application demonstrating common patterns and best practices with a minimal dependency set: raw SQL via psycopg2, app factory + blueprints, simple auth, templates, JSON APIs, and production serving via Waitress.

## Quickstart

1) Create and activate a venv
- macOS/Linux: `python3 -m venv venv && source venv/bin/activate`
- Windows (cmd): `python -m venv venv && venv\Scripts\activate`
- Alternatively: `./activate.sh` (macOS/Linux)

2) Install dependencies
- `pip install -r requirements.txt`

3) Start a local PostgreSQL (recommended)
- `docker compose up -d`

4) Configure environment (`.env` in project root)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_showcase
SECRET_KEY=dev-change-me
FLASK_ENV=development
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

Optional (dev tools):
- Install linters: `pip install -r requirements-dev.txt`
- Lint: `ruff check .` (auto-fix: `ruff check . --fix`)

## Project Structure

```
app/
  __init__.py   # app factory, logging, blueprints
  config.py     # env-driven configuration
  db.py         # psycopg2 connection helpers
  auth.py       # hashing helpers + login_required
  routes.py     # views + API endpoints
  errors.py     # error handlers
  templates/    # Jinja templates
  static/       # CSS, images, JS
app.py          # development entrypoint (Flask built-in server)
wsgi.py         # production entrypoint (Waitress)
docker-compose.yml, init-db.sql  # dev database
requirements.txt                 # pinned deps
```

## Architecture

```mermaid
flowchart TD
  %% Nodes
  A[Client/Browser]
  J[Dev Server app.py]
  K[Waitress wsgi.py]
  B[Flask App]
  C[Blueprint main routes]
  D[Auth helpers]
  E["DB helper (psycopg2)"]
  F[Error handlers]
  G[Templates Jinja2]
  H[Static files]
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

## Request Flow (Login)

```mermaid
sequenceDiagram
  participant B as Browser
  participant F as Flask App
  participant R as Routes (Blueprint)
  participant A as Auth Helpers
  participant D as DB (psycopg2)
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
  participant D as DB (psycopg2)
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

- Routing with Blueprints and request hooks
- PostgreSQL integration using raw SQL (psycopg2)
- Jinja2 templates and static assets
- Minimal auth: register/login/logout and session management
- JSON endpoints for posts and a health check
- Structured logging suited for dev/prod

## API Endpoints

- `GET /api/posts` — List all posts
- `GET /api/posts/<id>` — Get a single post
- `GET /health` — Health check

## Configuration

- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — Set to a strong value in non-dev environments
- `FLASK_ENV=development` — Enables debug features locally

Notes:
- When `SECRET_KEY` is omitted, a random one is generated at start. This is fine for local dev but will invalidate sessions between restarts.
- Default `DATABASE_URL` matches the docker-compose service for convenience.

## Request Context (flask.g)

- Purpose: Per-request scratchpad for transient data shared across view functions, helpers, and templates.
- Scope: Context-local; each request gets its own `g` and it is cleared on teardown.
- Current user: `@main.before_app_request` sets `g.user` to a user row (or `None`) so views/templates can rely on it.
- DB connection: `app/db.py#get_db()` stores a connection in `g.db` for reuse within the request; `close_db()` closes it in `app.teardown_appcontext`.
- Templates: `base.html`, `index.html`, `posts/*`, and `auth/profile.html` read `g.user` to toggle UI and show user details.
- Guidance: Store only request-scoped data; do not use `g` for cross-request state or persistence.

### SECRET_KEY Usage

- Purpose: Used by Flask to sign session cookies and flashed messages.
- Where set: `app/config.py` (`SECRET_KEY` from env or random fallback).
- Where loaded: `app/__init__.py` via `app.config.from_object(Config)`.
- Where exercised: session access in `app/auth.py` and `app/routes.py`, and `flash()`/`get_flashed_messages()` in views/templates.
- Caveat: No CSRF extension is configured; `SECRET_KEY` is not used for CSRF tokens here.
- Stability: If the key changes between runs (e.g., using the random fallback), existing sessions and flashes become invalid after restart.

## Using Docker Compose

- `docker compose up -d` starts a local PostgreSQL at port 5432
- Schema initialization: applied automatically on first start from `init-db.sql` via the container's `docker-entrypoint-initdb.d/` mechanism.
- Reapplying schema: either reset volumes (`docker compose down -v`) and start again, or run one of the manual `psql` commands above.
- Stop and remove containers: `docker compose down`
- Reset volumes: `docker compose down -v`

## Troubleshooting

- psycopg2 on Windows: ensure `pip` is up to date, then install `psycopg2-binary`.
- Env not loading: ensure `.env` is at project root and readable; we use `python-dotenv`.
- DB connection failures: verify `DATABASE_URL` and that PostgreSQL is running (`docker compose ps`).

## Security Notes

- Never commit secrets; use `.env` or a secrets manager.
- Use a strong `SECRET_KEY` in staging/production.
- Prefer running behind a production WSGI server like Waitress or Gunicorn.

## Linting

- Ruff is configured via `pyproject.toml`.
- Install dev tools: `pip install -r requirements-dev.txt`
- Lint: `ruff check .` (auto-fix: `ruff check . --fix`)
- Format: `ruff format` (or `--check` to verify only)

## CSS

- Location: `app/static/style.css` (linked in `app/templates/base.html`).
- Structure: Single file with clear sections and comments:
  1) Theme variables, 2) Base + reset, 3) Layout, 4) Components, 5) Utilities, 6) Responsiveness & a11y helpers.
- Theming: Centralized CSS variables under `:root` (e.g., `--color-brand`, `--space-2`, `--radius-sm`). Override these to adjust colors, spacing, and radii app‑wide.
- Components: Lightweight, semantic classes (`.btn`, `.card`, `.alert`, `.jumbotron`) with minimal specificity. Buttons use CSS custom properties (`--btn-bg`, `--btn-bg-hover`) to simplify variants like `.btn-secondary`.
- Layout: Simple container, flex rows/columns (`.row`, `.col-md-6`, `.col-md-8`) and a responsive CSS grid for posts (`.posts-grid`). Columns collapse to 100% width below 768px.
- Utilities: Small helpers like `.mt-4`, `.mb-3`, `.justify-content-center` for quick spacing/alignment without adding component bloat.
- Accessibility: Uses `:focus-visible` outlines, legible default line-height, and a `prefers-reduced-motion` media query to disable motion for users who prefer it.

Customization tips:
- Change theme: adjust variables in the `:root` block (e.g., `--color-brand`, `--color-bg`).
- Button variants: create a new class, e.g., `.btn-success { --btn-bg: #198754; --btn-bg-hover: #146c43; }` — no extra CSS needed beyond variables.
- Spacing scale: prefer `var(--space-*)` over hardcoded values to keep vertical rhythm consistent.
- New components: follow existing patterns (low specificity, rem spacing, variables for colors) and co‑locate styles within the Components section.

## Blueprints

- What: Blueprints are modular collections of routes, templates, and static files that can be registered on an app. They keep related views together and make large apps maintainable.
- Where: This project defines a single blueprint `main` in `app/routes.py`.
- Registration: The blueprint is registered in `app/__init__.py` inside `create_app()`.
- Contents: `main` contains server-rendered pages (index, posts, auth forms) and JSON APIs (`/api/posts`, `/api/posts/<id>`), plus a `/health` endpoint.
- Lifecycle hook: `@main.before_app_request` loads the current user into `g.user` so every view/template can rely on it being set or None.

Adding routes:
- Define a function and decorate it with `@main.route("/path")` in `app/routes.py`.
- Protect a route by stacking `@login_required` above the view (imported from `app.auth`).
- Return templates with `render_template(...)` or JSON/dicts for API responses.

## Code Logic Overview

- App factory: `app/__init__.py#create_app()` builds the Flask app, loads `Config`, configures logging, registers the `main` blueprint and error handlers, and wires the DB teardown.
- Config: `app/config.py` loads `.env` and exposes defaults for `SECRET_KEY` and `DATABASE_URL`. In non-dev, set `SECRET_KEY` explicitly.
- Database: `app/db.py` provides `get_db()` which opens one psycopg2 connection per request and stores it in `flask.g`. Rows use `RealDictCursor` so templates and JSON can access columns by name. Schema initialization is not handled in code; run `init-db.sql` manually.
- Auth: `app/auth.py` wraps Werkzeug’s hashing and provides `login_user`, `logout_user`, and `login_required`. The session only stores `user_id`, and the request hook populates `g.user`.
- Routes: `app/routes.py` contains the `main` blueprint. Key endpoints:
  - `/` — list recent posts
  - `/register` — create user with hashed password
  - `/login` and `/logout` — manage session
  - `/profile` — requires login
  - `/posts`, `/posts/create`, `/posts/<id>` — list/create/view posts
  - `/api/posts`, `/api/posts/<id>` — JSON APIs
  - `/health` — readiness probe
- Errors: `app/errors.py` registers 404 and 500 handlers that log and render friendly pages.
- Entrypoints: `app.py` runs the dev server; `wsgi.py` serves via Waitress for production-like environments.

## View Wrappers (Decorators)

- What: Python decorators wrap a view function, letting you run code before/after the view executes. We use this to enforce authentication.
- Where: `app/auth.py#login_required` returns a wrapper that checks whether the request is authenticated and redirects to `main.login` if not, otherwise it calls the original view with `*args, **kwargs`.
- How: The decorator defines an inner `wrapper(*args, **kwargs)` that performs the check and either returns `redirect(...)` or `view(*args, **kwargs)`. Early returns short‑circuit the original view.
- `functools.wraps`: Preserves the original function’s `__name__`, `__doc__`, and other metadata. This keeps Flask endpoint names and debugging tracebacks accurate, and avoids confusing names like `wrapper` in `url_for()` and logs.
- Order: Decorators apply bottom‑up. Using `@main.route(...)` above `@login_required` is common and works because `wraps` preserves metadata. Keep a consistent order across views for readability.
- Auth source: Authentication state is populated in a request hook (`@main.before_app_request`) which sets `g.user`; `login_required` prefers `g.user` and falls back to `session['user_id']`.
