from flask import Flask, jsonify
from routes import api_bp

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)