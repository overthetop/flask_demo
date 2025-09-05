"""Development entrypoint.

Run a local development server. Initialize the database schema manually by
executing `init-db.sql` against your PostgreSQL instance (see README).
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Run the application
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development",
    )
