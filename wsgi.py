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
