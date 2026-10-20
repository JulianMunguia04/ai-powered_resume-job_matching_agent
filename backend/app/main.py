from flask import Flask, jsonify

from routes import api_bp

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Hello from the Flask backend!"})

# Health Check
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    }), 200

# Favicon ignore
@app.route('/favicon.ico')
def favicon():
    return '', 204

# API Routes
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(
        host="127.0.0.1", 
        port=5000, 
        debug=True
    )

# python backend/app/main.py from root folder to run