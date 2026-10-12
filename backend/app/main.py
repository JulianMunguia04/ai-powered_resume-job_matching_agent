from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Hello from the Flask backend!"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)