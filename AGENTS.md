# Repository Guidelines

## Project Structure & Module Organization
- app/: Flask application package. Key modules: `__init__.py` (factory), `routes.py` (Blueprint `main`), `db.py` (PostgreSQL helpers), `auth.py` (auth helpers), `config.py` (env config), `errors.py` (handlers).
- app/templates/ and app/static/: Jinja2 templates and assets.
- app.py: Dev entry point (Flask built‑in server).
- wsgi.py: Production entry (Waitress).
- requirements.txt: Python deps. docker-compose.yml + init-db.sql: local PostgreSQL setup.

## Build, Test, and Development Commands
- Create venv: macOS/Linux `python3 -m venv venv && source venv/bin/activate`; Windows (cmd) `python -m venv venv && venv\Scripts\activate`; or `./activate.sh` (Unix).
- Install deps: `pip install -r requirements.txt`.
- Start DB (dev): `docker compose up -d` (exposes Postgres on 5432; default creds match compose). On first start, the container auto-applies `init-db.sql`.
- Set env: create `.env` with `DATABASE_URL`, `SECRET_KEY`, `FLASK_DEBUG=1` (for dev; defaults fit compose).
- Init DB schema: Docker Compose auto-applies `init-db.sql` on first start. Alternatively, run it manually via `psql` (see README for commands).
- Run (dev): `python app.py` → http://localhost:5000
- Run (Waitress): `python wsgi.py` → http://localhost:8000
- Lint: `ruff check .` (auto-fix: `ruff check . --fix`)
 - Install dev tools: `pip install -r requirements-dev.txt`

## Coding Style & Naming Conventions
- Python: PEP 8, 4‑space indent, `snake_case` for functions/vars, `UPPER_CASE` for constants, modules in `lower_snake_case`.
- Routes: keep view function names descriptive (e.g., `create_post`, `api_posts`).
- Logging: use `current_app.logger` with appropriate levels (debug/info/warning).
- Templates: place under `app/templates/…` mirroring view paths (e.g., `posts/create.html`).

Docstrings & Comments:
- Add a short module docstring describing purpose (done across core modules).
- Prefer concise function docstrings describing behavior and side effects.
- Keep inline comments focused on “why” rather than “what”.

## Testing Guidelines
- No formal test suite yet. If adding tests, prefer `pytest` with files named `tests/test_*.py` and aim for coverage on routes, auth, and db helpers.
- Local run: `pytest` (after adding `pytest` to dev deps).

## Commit & Pull Request Guidelines
- Commits: concise, imperative summaries (e.g., “add posts list view”); include details in the body if needed.
- PRs: clear description, link related issues, steps to reproduce/verify, screenshots for UI, and notes on DB changes (migrations/seed data). Keep diffs focused and include docs updates when relevant.

## Security & Configuration Tips
- Never commit secrets; use `.env` loaded by `python-dotenv`.
- Use strong `SECRET_KEY` in non‑dev environments and a proper `DATABASE_URL`.
- Prefer Waitress (or WSGI server) for deployment; avoid Flask debug in production.

## Blueprints & Routes
- Single blueprint `main` in `app/routes.py`. Register in `create_app()`.
- Use `@main.before_app_request` to load `g.user` per request.
- Protect views with `@login_required` (from `app.auth`).
- SQL uses psycopg with the `dict_row` row factory for dict-like rows.

## Docs & Diagrams
- README includes a high-level architecture diagram and two Mermaid sequence diagrams (Login, Create Post).
- README also contains Quickstart, Configuration, and Troubleshooting aligned with this guide.

## Linting
- We use Ruff (configured in `pyproject.toml`). Install locally with `pip install ruff`.
- Command examples:
  - `ruff check .` — run static analysis
  - `ruff check . --fix` — apply safe automatic fixes
  - `ruff format` — optional formatter if you prefer Ruff as a formatter
 - CI: GitHub Actions runs `ruff check` and `ruff format --check` in `.github/workflows/lint.yml`.
