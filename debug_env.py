import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
load_dotenv()

# Print environment variables to debug
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
print("FLASK_ENV:", os.getenv("FLASK_ENV"))

# Test if we can connect to the database

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    print("Successfully connected to the database!")
    conn.close()
except Exception as e:
    print(f"Failed to connect to the database: {e}")
