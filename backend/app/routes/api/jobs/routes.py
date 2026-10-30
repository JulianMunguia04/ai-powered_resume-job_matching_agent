# Routes for /jobs

from uuid import uuid4

from flask import Blueprint, render_template, jsonify, request, abort

from services.embeddings import embed_text, MODEL_NAME
from services.job_analyzer import analyze_job
from services.requirement_matching import match_job_requirements

from ..resumes.routes import resumes

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

    analysis = analyze_job(description.strip())

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
        "embedding_model": MODEL_NAME,
        "analysis": analysis,
    }

    jobs[job_id] = job

    # Do not send the entire embedding vector to the client.
    return jsonify({
        "job": {
            **public_job(job),
            "analysis": analysis,
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

# POST /jobs/match
# Match a stored resume against all stored jobs.
@jobs_bp.route("/match", methods=["POST"])
def match_jobs():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    resume_id = data.get("resume_id")

    if not isinstance(resume_id, str) or not resume_id.strip():
        return jsonify({
            "error": "A non-empty resume_id is required."
        }), 400

    # 1. Retrieve the previously embedded resume.
    resume = resumes.get(resume_id.strip())

    if resume is None:
        return jsonify({
            "error": "Resume not found."
        }), 404

    # 2. Verify the resume uses the expected embedding model.
    if resume["embedding_model"] != MODEL_NAME:
        return jsonify({
            "error": "Resume embedding model does not match."
        }), 400

    resume_embedding = resume["embedding"]

    # 3. Compare the resume against every stored job.
    matches = []

    for job in jobs.values():
        if job["embedding_model"] != resume["embedding_model"]:
            continue

        job_embedding = job["embedding"]

        if len(resume_embedding) != len(job_embedding):
            continue

        # Both vectors are normalized, so their dot product
        # is equivalent to cosine similarity.
        similarity = sum(
            resume_value * job_value
            for resume_value, job_value
            in zip(resume_embedding, job_embedding)
        )

        matches.append({
            "job_id": job["id"],
            "title": job["title"],
            "description": job["description"],
            "similarity_score": round(float(similarity), 4)
        })

    # 4. Sort from highest to lowest similarity.
    matches.sort(
        key=lambda match: match["similarity_score"],
        reverse=True
    )

    # 5. Return the ranked jobs.
    return jsonify({
        "resume_id": resume["id"],
        "total_matches": len(matches),
        "matches": matches
    }), 200

# Analyze job to resume
@jobs_bp.route("/match-requirements", methods=["POST"])
def match_requirements():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    resume_id = data.get("resume_id")
    job_id = data.get("job_id")

    if not isinstance(resume_id, str) or not resume_id.strip():
        return jsonify({"error": "A non-empty resume_id is required."}), 400

    if not isinstance(job_id, str) or not job_id.strip():
        return jsonify({"error": "A non-empty job_id is required."}), 400

    resume = resumes.get(resume_id.strip())
    if resume is None:
        return jsonify({"error": "Resume not found."}), 404

    job = jobs.get(job_id.strip())
    if job is None:
        return jsonify({"error": "Job not found."}), 404

    resume_analysis = resume.get("analysis")
    job_analysis = job.get("analysis")

    if not resume_analysis or not job_analysis:
        return jsonify({
            "error": "Resume or job analysis is unavailable."
        }), 400

    result = match_job_requirements(
        resume_analysis,
        job_analysis,
    )

    return jsonify({
        "resume_id": resume["id"],
        "job": {
            "id": job["id"],
            "title": job["title"],
        },
        "matching": result,
    }), 200

# Helper Functions

def public_job(job):
    return {
        "id": job["id"],
        "title": job["title"],
        "description": job["description"],
        "embedding_model": job["embedding_model"],
        "embedding_dimensions": len(job["embedding"])
    }