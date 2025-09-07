# Gemini Project Analysis

This document provides a summary of the project's structure, technologies, and common commands to facilitate development and maintenance.

## 1. Project Overview

This is a Python-based web application built with the Flask framework. It serves as a showcase application demonstrating common web development patterns, including:
- A simple blog/post system.
- User authentication (registration, login, logout).
- A combination of server-rendered HTML pages (via Jinja2) and a JSON API.
- A structured application layout using the app factory pattern and Blueprints.

The application is configured to run against a PostgreSQL database and can be served either with the Flask development server or a production-ready WSGI server (Waitress).

## 2. Tech Stack

- **Language:** Python (Target version is 3.12, as per `pyproject.toml`)
- **Web Framework:** Flask
- **Database:** PostgreSQL (via `psycopg[binary]`)
- **WSGI Server:** Waitress
- **Linting & Formatting:** Ruff
- **Dependency Management:** Pip with `requirements.txt` and `requirements-dev.txt`.
- **Environment Configuration:** `python-dotenv` for loading variables from a `.env` file.

## 3. Project Structure

The project follows a standard Flask application structure:

- `app.py`: The entrypoint for running the local development server.
- `wsgi.py`: The entrypoint for running the application with a production WSGI server like Waitress.
- `app/`: The main Python package containing the core application logic.
  - `__init__.py`: Implements the **app factory pattern** (`create_app`), which constructs the Flask app instance, registers blueprints, and initializes extensions.
  - `routes.py`: Defines a Flask **Blueprint** containing all application routes, including HTML pages and API endpoints.
  - `db.py`: Manages the PostgreSQL database connection lifecycle, scoping it to the request context.
  - `auth.py`: Contains helpers for password hashing and a `@login_required` decorator to protect routes.
  - `config.py`: Manages configuration loaded from environment variables.
  - `errors.py`: Defines custom error handlers for 404 and 500 errors.
  - `templates/`: Directory for all Jinja2 HTML templates.
  - `static/`: Directory for CSS, JavaScript, and other static assets.
- `init-db.sql`: The SQL script used to create the database schema.
- `requirements.txt`: A list of Python dependencies for the application to run.
- `requirements-dev.txt`: A list of additional dependencies for development, such as linters.
- `pyproject.toml`: Configuration file for tools, primarily `ruff`.
- `.github/workflows/lint.yml`: GitHub Actions workflow for running the linter on pushes and pull requests.

## 4. Setup and Installation

1.  **Create Virtual Environment:**
    ```sh
    python -m venv .venv
    ```
2.  **Activate Environment:**
    - Windows: `.\.venv\Scripts\activate`
    - macOS/Linux: `source .venv/bin/activate`
3.  **Install Dependencies:**
    ```sh
    pip install -r requirements.txt -r requirements-dev.txt
    ```
4.  **Configure Environment:**
    - Create a `.env` file in the project root.
    - Add the following required variables:
      ```
      DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_showcase
      SECRET_KEY=a-strong-and-secret-key-for-development
      FLASK_DEBUG=1
      ```

## 5. Running the Application

- **Development Server:**
  ```sh
  python app.py
  ```
  The application will be available at `http://localhost:5000`.

- **Production-like Server (Waitress):**
  ```sh
  python wsgi.py
  ```
  The application will be available at `http://localhost:8000`.

## 6. Code Quality and Linting

The project uses **Ruff** for linting and formatting. The configuration is in `pyproject.toml`.

- **Check for linting errors:**
  ```sh
  ruff check .
  ```
- **Check for formatting issues:**
  ```sh
  ruff format --check .
  ```
- **Apply formatting fixes:**
  ```sh
  ruff format .
  ```

The CI pipeline defined in `.github/workflows/lint.yml` runs these checks automatically.

## 7. Testing

The presence of a `.pytest_cache` directory indicates that **Pytest** is the testing framework. However, no test files are present in the visible directory structure.

- **To run tests (if any are added):**
  ```sh
  pytest
  ```

## 8. Database

- **Type:** PostgreSQL
- **Connection:** Managed by `app/db.py` and configured via the `DATABASE_URL` environment variable.
- **Schema Initialization:** The application code does **not** handle database initialization. The schema must be created by manually executing the `init-db.sql` script against the database. The `README.md` provides instructions for doing this with `docker compose` or `psql`.
