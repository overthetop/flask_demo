# Flask Showcase Tutorial

This tutorial will guide you through understanding the Flask Showcase application. We'll explain Flask concepts, project structure, and related technologies step by step.

## Table of Contents
1. [What is Flask?](#what-is-flask)
2. [Project Overview](#project-overview)
3. [Key Flask Concepts](#key-flask-concepts)
4. [Project Structure Walkthrough](#project-structure-walkthrough)
5. [Database Integration](#database-integration)
6. [Authentication System](#authentication-system)
7. [Templates and Frontend](#templates-and-frontend)
8. [API Endpoints](#api-endpoints)
9. [Production Deployment](#production-deployment)
10. [Running the Application](#running-the-application)
11. [Learning Exercises](#learning-exercises)

## What is Flask?

Flask is a lightweight web framework for Python. It's designed to make getting started quick and easy, with the ability to scale up to complex applications. Flask is called a microframework because it doesn't require particular tools or libraries.

### Key Features of Flask:
- Built-in development server and debugger
- Integrated support for unit testing
- RESTful request dispatching
- Jinja2 templating engine
- Secure cookies support
- Unicode based

### Why Flask?
Flask is great for beginners because:
1. It's simple and easy to understand
2. It doesn't impose many restrictions on how you should structure your application
3. It has excellent documentation
4. It's widely used in the industry

## Project Overview

This Flask Showcase application demonstrates key web development concepts:
- User authentication (registration, login, logout)
- Database integration with PostgreSQL
- Template rendering with Jinja2
- RESTful API endpoints
- Error handling
- Session management
- Comprehensive logging

The application allows users to register, log in, create posts, and view posts from other users.

## Key Flask Concepts

### 1. Application Factory Pattern
Instead of creating a Flask application instance globally, we use the application factory pattern. This approach:
- Makes testing easier
- Allows for multiple application instances
- Provides better organization

```python
# app/__init__.py
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints, error handlers, etc.
    return app
```

### 2. Blueprints
Blueprints help organize routes into separate modules. Our main blueprint is defined in `app/routes.py`:

```python
# app/routes.py
main = Blueprint('main', __name__)
```

### 3. Request Hooks
Request hooks run code before or after requests:
```python
@main.before_app_request
def load_logged_in_user():
    # This runs before every request
    pass
```

### 4. Template Inheritance
We use a base template that other templates extend:
```html
<!-- templates/base.html -->
<!doctype html>
<html>
  <head>
    <title>{% block title %}{% endblock %} - Flask Showcase</title>
  </head>
  <body>
    {% block content %}{% endblock %}
  </body>
</html>
```

## Project Structure Walkthrough

Let's examine each file and directory:

### Root Directory Files
1. **app.py** - Development entry point
2. **wsgi.py** - Production entry point (for Waitress)
3. **requirements.txt** - Python dependencies
4. **.gitignore** - Files to ignore in version control
5. **.flake8** - Code style configuration
6. **README.md** - Project documentation

### App Directory
The `app/` directory contains all application code:

1. **`__init__.py`** - Application factory
2. **auth.py** - Authentication utilities
3. **config.py** - Configuration settings
4. **db.py** - Database connection and setup
5. **errors.py** - Error handlers
6. **routes.py** - Route definitions
7. **templates/** - HTML templates

## Database Integration

Our application uses PostgreSQL for both development and production.

### Database Connection
The `get_db()` function in `app/db.py` creates database connections:

```python
def get_db():
    if 'db' not in g:
        database_url = current_app.config['DATABASE_URL']
        # PostgreSQL connection
        g.db = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return g.db
```

### Database Schema
We have two tables:
1. **users** - Stores user information
2. **posts** - Stores blog posts

The `init_db()` function creates these tables if they don't exist.

## Authentication System

Flask doesn't include authentication by default, so we implement our own:

### Password Hashing
We use Werkzeug's security functions to hash passwords:
```python
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)
```

### Session Management
We store user IDs in Flask sessions:
```python
def login_user(user_id):
    session.clear()
    session['user_id'] = user_id

def logout_user():
    session.clear()
```

### Login Required Decorator
We created a decorator to protect routes:
```python
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            # Redirect to login page
            return redirect(url_for('main.login'))
        return view(**kwargs)
    return wrapped_view
```

## Templates and Frontend

Flask uses Jinja2 as its template engine. Templates are HTML files with special syntax for dynamic content.

### Template Inheritance
Our base template (`templates/base.html`) defines the overall structure:
```html
<html>
  <head>
    <title>{% block title %}{% endblock %} - Flask Showcase</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  </head>
  <body>
    <header><!-- Navigation bar --></header>
    <main>
      <div class="container">
        <!-- Flash messages -->
        {% block content %}{% endblock %}
      </div>
    </main>
  </body>
</html>
```

### Child Templates
Other templates extend the base template:
```html
{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
  <h1>Welcome to Flask Showcase</h1>
  <!-- Page-specific content -->
{% endblock %}
```

### Template Variables
We pass data from routes to templates:
```python
# In routes.py
return render_template('index.html', posts=posts)

# In templates/index.html
{% for post in posts %}
  <h2>{{ post.title }}</h2>
  <p>{{ post.content }}</p>
{% endfor %}
```

### Styling
Instead of using Bootstrap, we've implemented our own minimal CSS framework in `app/static/style.css`. This provides clean, readable styling with:
- Responsive navigation
- Card-based layouts for content
- Simple form styling
- Alert messages for user feedback
- A consistent color scheme and typography

This approach keeps the application lightweight while maintaining good usability and readability.

## API Endpoints

The application includes RESTful API endpoints that return JSON:

```python
@main.route('/api/posts')
def api_posts():
    # Get posts from database
    posts = get_posts_from_db()
    
    # Return JSON response
    return {'posts': posts_list}
```

These endpoints can be used by frontend JavaScript or other applications.

## Production Deployment

For production, we use Waitress as the WSGI server instead of Flask's development server.

### WSGI Entry Point
`wsgi.py` is the standard entry point for WSGI servers:
```python
from app import create_app
from waitress import serve
import os

app = create_app()

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on {host}:{port}")
    serve(app, host=host, port=port)
```

## Running the Application

### Development Mode
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_showcase
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   ```

4. Initialize the database:
   ```bash
   python -m flask init-db
   ```

5. Run the development server:
   ```bash
   python app.py
   ```

6. Visit `http://localhost:5000` in your browser

### Production Mode
1. Set up PostgreSQL database (see README)
2. Update `.env` with PostgreSQL connection string
3. Run with Waitress:
   ```bash
   python wsgi.py
   ```

4. Visit `http://localhost:8000` in your browser

### 1. Add a new route - Create a new page in `routes.py`
2. **Modify a template** - Change the design of an existing page
3. **Add a new database table** - Extend the database schema
4. **Create a new API endpoint** - Add a JSON endpoint
5. **Implement form validation** - Add validation to existing forms

## Common Flask Patterns

### 1. Handling Forms
```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Process form data
        username = request.form['username']
        # ... validation and processing
    else:
        # Show form
        return render_template('register.html')
```

### 2. Error Handling
```python
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
```

### 3. Flash Messages
```python
# In routes.py
flash('Registration successful!')

# In templates
{% with messages = get_flashed_messages() %}
  {% if messages %}
    {% for message in messages %}
      <div class="alert">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

## Next Steps

To continue learning Flask:

1. **Read the Flask Documentation** - https://flask.palletsprojects.com/
2. **Try Flask Extensions** - SQLAlchemy for ORM, Flask-WTF for forms
3. **Learn About Testing** - Write tests for your Flask applications
4. **Explore Deployment Options** - Heroku, Docker, cloud platforms
5. **Study Security Best Practices** - CSRF protection, XSS prevention

This tutorial covered the fundamentals of the Flask Showcase application. As you work with the code, refer back to these concepts to deepen your understanding of Flask and web development.