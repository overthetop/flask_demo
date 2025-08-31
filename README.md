# Flask Showcase Application

This is an educational Flask application demonstrating popular features and best practices. It showcases how to build a production-ready Flask application with PostgreSQL (without ORM), user authentication, templates, RESTful APIs, and comprehensive logging.

## Features

- Flask routing and HTTP methods (GET, POST)
- PostgreSQL database integration (without ORM)
- Template rendering with Jinja2
- User authentication (login/logout)
- Session management
- Form handling
- Static file serving
- Error handling
- RESTful API endpoints
- Health check endpoint
- Comprehensive application logging

## Architecture

```mermaid
graph TD
    A[Client/Browser] --> B[Flask Application]
    B --> C[Routes Handler]
    C --> D[Authentication Module]
    C --> E[Database Module]
    C --> F[Error Handlers]
    E --> G[(PostgreSQL Database)]
    B --> H[Templates Engine]
    H --> I[HTML Templates]
    B --> J[Static Files]
    B --> K[Waitress Server]
    
    subgraph FlaskApp [Flask Application]
        B
        C
        D
        E
        F
        H
        J
    end
    
    subgraph External [External Components]
        G
        K
    end
```

## Project Structure

```
flask-showcase/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── db.py                # Database connection and setup
│   ├── auth.py              # Authentication utilities
│   ├── routes.py            # Route definitions
│   ├── errors.py            # Error handlers
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, images
├── requirements.txt         # Python dependencies
├── wsgi.py                 # WSGI entry point for production
├── .env                     # Environment variables (not in repo)
├── .gitignore               # Git ignore rules
└── app.py                   # Development entry point
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   # On Windows, you might need to install psycopg2-binary separately first:
   pip install psycopg2-binary
   pip install -r requirements.txt
   ```
   
   Note: If you encounter issues with `psycopg2-binary` on Windows, make sure you have the latest pip version:
   ```bash
   python -m pip install --upgrade pip
   pip install psycopg2-binary
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database:

   Option A - Manual setup:
   ```sql
   CREATE DATABASE flask_showcase;
   CREATE USER flask_user WITH PASSWORD 'flask_pass';
   GRANT ALL PRIVILEGES ON DATABASE flask_showcase TO flask_user;
   ```
   
   Then initialize the database tables using the provided SQL script:
   ```bash
   psql -U flask_user -d flask_showcase -f init-db.sql
   ```

   Option B - Using Docker Compose (recommended for development):
   ```bash
   # Start PostgreSQL in the background
   # The database tables will be automatically created
   docker compose up -d
   
   # Check that the database is running
   docker compose ps
   ```

4. Create a `.env` file in the project root with:
   ```env
   DATABASE_URL=postgresql://flask_user:flask_pass@localhost/flask_showcase
   SECRET_KEY=your-secret-key-here-change-in-production
   FLASK_ENV=development
   ```
   
   If using Docker Compose, use these credentials instead:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_showcase
   SECRET_KEY=your-secret-key-here-change-in-production
   FLASK_ENV=development
   ```

5. Initialize the database (skip this step if using Docker Compose):
   ```bash
   python -c "from app import create_app; from app.db import init_db; app = create_app(); with app.app_context(): init_db(); print('Database initialized successfully!')"
   ```

6. Run the application in development mode:
   ```bash
   python app.py
   ```

7. Or run with Waitress for production:
   ```bash
   python wsgi.py
   ```

8. Visit `http://localhost:8000` in your browser (Waitress) or `http://localhost:5000` (development)

## API Endpoints

- `GET /api/posts` - Get all posts as JSON
- `GET /api/posts/<id>` - Get a specific post as JSON
- `GET /health` - Health check endpoint

## Key Flask Concepts Demonstrated

1. **Application Factory Pattern** - Creates the Flask app instance
2. **Blueprints** - Organize routes into separate modules
3. **Request Hooks** - `before_app_request` for loading user data
4. **Template Inheritance** - Base template with blocks for child templates
5. **Flash Messages** - User feedback mechanism
6. **Session Management** - User login state
7. **Error Handlers** - Custom error pages
8. **Database Integration** - Raw SQL with PostgreSQL
9. **Environment Configuration** - Loading settings from `.env`
10. **CLI Commands** - Custom `flask init-db` command
11. **Logging** - Comprehensive application logging

## Best Practices Implemented

- Separation of concerns with modular structure
- Environment-based configuration
- Secure password hashing
- Database connection management
- Error handling and user feedback
- Input validation
- Protection against common web vulnerabilities
- RESTful API design
- Production-ready deployment with Waitress
- Comprehensive logging for monitoring and debugging

## Using Docker Compose

This project includes Docker Compose configuration for easily setting up a PostgreSQL database for development.

- `docker-compose.yml` - Defines the PostgreSQL service and automatically initializes the database
- `init-db.sql` - SQL script to create the required tables

To use Docker Compose:

1. Start the database:
   ```bash
   docker compose up -d
   ```

2. The database tables will be automatically created when the container starts.

3. When you're done, stop the database:
   ```bash
   docker compose down
   ```

If you want to reset the database, you can remove the volume and start fresh:
```bash
docker compose down -v
docker compose up -d
```