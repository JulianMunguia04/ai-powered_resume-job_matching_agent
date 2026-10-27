from uuid import uuid4

from flask import Blueprint, jsonify, request

from services.embeddings import embed_text, MODEL_NAME

resumes_bp = Blueprint("resumes", __name__)

resumes = {}

@resumes_bp.route("/", methods=["POST"])
def create_resume():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify({
            "error": "Non-empty resume text is required."
        }), 400

    resume_id = str(uuid4())
    resume_text = text.strip()

    # Generate the embedding once, when the resume is submitted.
    embedding = embed_text(resume_text)

    resume = {
        "id": resume_id,
        "text": resume_text,
        "embedding": embedding,
        "embedding_model": MODEL_NAME,
    }

    resumes[resume_id] = resume

    # Keep the actual vector private.
    return jsonify({
        "resume": {
            "id": resume_id,
            "embedding_model": MODEL_NAME,
            "embedding_dimensions": len(embedding),
        }
    }), 201


@resumes_bp.route("/", methods=["GET"])
def get_all_resumes():
    return jsonify({
        "resumes": [
            {
                "id": resume["id"],
                "embedding_model": resume["embedding_model"],
                "embedding_dimensions": len(resume["embedding"]),
            }
            for resume in resumes.values()
        ]
    }), 200