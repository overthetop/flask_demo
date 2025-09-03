# Repository Guidelines

## Project Structure & Module Organization
- app/: Flask application package. Key modules: `__init__.py` (factory), `routes.py` (Blueprint `main`), `db.py` (PostgreSQL + CLI), `auth.py` (auth helpers), `config.py` (env config), `errors.py` (handlers).
- app/templates/ and app/static/: Jinja2 templates and assets.
- app.py: Dev entry point (Flask built‑in server).
- wsgi.py: Production entry (Waitress).
- requirements.txt: Python deps. docker-compose.yml + init-db.sql: local PostgreSQL setup.

## Build, Test, and Development Commands
- Create venv: `python -m venv venv` then Windows `venv\Scripts\activate`, macOS/Linux `source venv/bin/activate`.
- Install deps: `pip install -r requirements.txt` (Windows may also need `pip install psycopg2-binary`).
- Start DB (dev): `docker compose up -d` (uses credentials from compose).
- Set env: `.env` with `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=development`.
- Init DB: `flask --app app:create_app init-db` (registers tables via app CLI).
- Run (dev): `python app.py` → http://localhost:5000
- Run (prod-ish): `python wsgi.py` (Waitress) → http://localhost:8000

## Coding Style & Naming Conventions
- Python: PEP 8, 4‑space indent, `snake_case` for functions/vars, `UPPER_CASE` for constants, modules in `lower_snake_case`.
- Routes: keep view function names descriptive (e.g., `create_post`, `api_posts`).
- Logging: use `current_app.logger` with appropriate levels (debug/info/warning).
- Templates: place under `app/templates/…` mirroring view paths (e.g., `posts/create.html`).

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
