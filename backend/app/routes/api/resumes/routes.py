
from uuid import UUID

from flask import Blueprint, jsonify, request

from services.embeddings import embed_text, MODEL_NAME
from services.resume_analyzer import analyze_resume
from services.database import db
from models import Resume, Embedding

resumes_bp = Blueprint("resumes", __name__)


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

    resume_text = text.strip()

    try:
        # Analyze the resume.
        analysis = analyze_resume(resume_text)

        # Generate its embedding.
        embedding_vector = embed_text(resume_text)

        # Store the embedding.
        embedding_record = Embedding(
            model_name=MODEL_NAME,
            dimensions=len(embedding_vector),
            embedding=embedding_vector
        )

        db.session.add(embedding_record)
        db.session.flush()

        # Store the resume and link it to its embedding.
        resume = Resume(
            embedding_id=embedding_record.id,
            raw_text=resume_text,
            analysis=analysis
        )

        db.session.add(resume)
        db.session.commit()

        return jsonify({
            "resume": {
                "id": str(resume.id),
                "embedding_model": embedding_record.model_name,
                "embedding_dimensions": embedding_record.dimensions,
                "analysis": analysis
            }
        }), 201

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "error": "Failed to create resume.",
            "details": str(error)
        }), 500


@resumes_bp.route("/", methods=["GET"])
def get_all_resumes():
    resumes = Resume.query.order_by(
        Resume.created_at.desc()
    ).all()

    return jsonify({
        "resumes": [
            {
                "id": str(resume.id),
                "embedding_model": resume.embedding_record.model_name,
                "embedding_dimensions": resume.embedding_record.dimensions
            }
            for resume in resumes
        ]
    }), 200


@resumes_bp.route("/<resume_id>", methods=["GET"])
def get_resume(resume_id):
    try:
        parsed_id = UUID(resume_id)
    except ValueError:
        return jsonify({
            "error": "Resume not found."
        }), 404

    resume = db.session.get(Resume, parsed_id)

    if resume is None:
        return jsonify({
            "error": "Resume not found."
        }), 404

    return jsonify({
        "resume": {
            "id": str(resume.id),
            "text": resume.raw_text,
            "embedding_model": resume.embedding_record.model_name,
            "embedding_dimensions": resume.embedding_record.dimensions,
            "analysis": resume.analysis
        }
    }), 200
