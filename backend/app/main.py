
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import URL, text
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

from services.database import db
from routes import api_bp

# Import models so SQLAlchemy registers all four tables.
from models import Embedding, Resume, Job, Matching


app = Flask(__name__)

# Build the database URL safely, including passwords
# containing special characters.
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Redis configuration.
redis_url = os.getenv("REDIS_URL")

if not redis_url:
    raise RuntimeError("REDIS_URL is not configured.")

# Initialize database.
db.init_app(app)

# Initialize Redis-backed rate limiter.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri=redis_url,
    headers_enabled=True,
)

# Register API routes.
app.register_blueprint(api_bp, url_prefix="/api")


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Hello from the Flask backend!"
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    }), 200


@app.route("/api/db-health", methods=["GET"])
def database_health():
    try:
        db.session.execute(text("SELECT 1"))

        return jsonify({
            "status": "ok",
            "message": "PostgreSQL connection successful"
        }), 200

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Database connection failed",
            "error": str(error)
        }), 500


@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        "error": "Too many requests.",
        "message": "You have exceeded the API rate limit. Please try again shortly."
    }), 429


if __name__ == "__main__":
    with app.app_context():
        # Enable pgvector in PostgreSQL.
        db.session.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )
        db.session.commit()

        # Create tables if they do not already exist.
        db.create_all()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

# Run from project root:
# python backend/app/main.py
