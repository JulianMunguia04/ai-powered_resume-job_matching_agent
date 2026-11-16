
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import URL, text

load_dotenv()

from services.database import db
from routes import api_bp

# Import models so SQLAlchemy registers all three tables.
from models import Embedding, Resume, Job


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

db.init_app(app)

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

# from root python backend/app/main.py