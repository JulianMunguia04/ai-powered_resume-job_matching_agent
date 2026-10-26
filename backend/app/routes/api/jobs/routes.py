# Routes for /jobs

from uuid import uuid4

from flask import Blueprint, render_template, jsonify, request, abort

from services.embeddings import embed_text, MODEL_NAME

jobs_bp = Blueprint('jobs', __name__)

# Temporary in-memory-storage (Records disappear when server restarts)
jobs = {}

# GET /jobs Returns all jobs
@jobs_bp.route('/', methods=['GET'])
def get_all_jobs():
    return jsonify({
        "jobs": [public_job(job) for job in jobs.values()]
    }), 200

# POST /jobs Validate and create a job
@jobs_bp.route('/', methods=['POST'])
def create_job():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    title = data.get("title")
    description = data.get("description")

    if not isinstance(title, str) or not title.strip():
        return jsonify({
            "error": "A non-empty title is required."
        }), 400

    if not isinstance(description, str) or not description.strip():
        return jsonify({
            "error": "A non-empty description is required."
        }), 400

    job_id = str(uuid4())

    # Generate an embedding from the job title and description.
    text_to_embed = f"{title.strip()}\n{description.strip()}"
    embedding = embed_text(text_to_embed)

    # Keep the embedding internally for future matching.
    job = {
        "id": job_id,
        "title": title.strip(),
        "description": description.strip(),
        "embedding": embedding,
        "embedding_model": MODEL_NAME
    }

    jobs[job_id] = job

    # Do not send the entire embedding vector to the client.
    return jsonify({
        "job": {
            "id": job["id"],
            "title": job["title"],
            "description": job["description"],
            "embedding_model": job["embedding_model"],
            "embedding_dimensions": len(embedding)
        }
    }), 201

# /jobs/[job_id] get job by id
@jobs_bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    """Return one job by its ID."""
    job = jobs.get(job_id)

    if job is None:
        return jsonify({
            "error": "Job not found."
        }), 404

    return jsonify({"job": public_job(job)}), 200

# Helper Functions

def public_job(job):
    return {
        "id": job["id"],
        "title": job["title"],
        "description": job["description"],
        "embedding_model": job["embedding_model"],
        "embedding_dimensions": len(job["embedding"])
    }