"""Development entrypoint.

Run a local development server. Use the Flask CLI command
`flask --app app:create_app init-db` to initialize the database schema.
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Run the application (use CLI `flask --app app:create_app init-db` to init DB)
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development",
    )
