from app import create_app, db
import os

app = create_app()

if __name__ == "__main__":
    # Initialize the database
    with app.app_context():
        db.init_db()

    # Run the application
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development",
    )
