"""Production entrypoint using Waitress.

This module exposes an app factory and runs the app via Waitress when invoked
directly. Configure `HOST`/`PORT` via environment variables.
"""

import os

from waitress import serve

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting server on {host}:{port}")
    serve(app, host=host, port=port)
