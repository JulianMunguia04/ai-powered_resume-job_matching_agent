# Routes for /jobs

from uuid import uuid4

from flask import Blueprint, jsonify, request

from services.embeddings import embed_text, MODEL_NAME
from services.job_analyzer import analyze_job
from services.requirement_matching import match_job_requirements
from services.hybrid_matching import (
    calculate_hybrid_matches,
    rerank_with_cross_encoder,
    evaluate_resume_job,
    SEMANTIC_WEIGHT,
    BM25_WEIGHT,
    STRUCTURED_WEIGHT,
)

from ..resumes.routes import resumes


jobs_bp = Blueprint("jobs", __name__)

# Temporary in-memory storage.
# Records disappear when the server restarts.
jobs = {}


# GET /jobs
# Return all stored jobs.
@jobs_bp.route("/", methods=["GET"])
def get_all_jobs():
    return jsonify({
        "jobs": [public_job(job) for job in jobs.values()]
    }), 200


# POST /jobs
# Validate and create a job.
@jobs_bp.route("/", methods=["POST"])
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

    title = title.strip()
    description = description.strip()

    # Analyze the job description.
    analysis = analyze_job(description)

    job_id = str(uuid4())

    # Generate an embedding from the job title and description.
    text_to_embed = f"{title}\n{description}"
    embedding = embed_text(text_to_embed)

    job = {
        "id": job_id,
        "title": title,
        "description": description,
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


# GET /jobs/<job_id>
# Return one job by ID.
@jobs_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    job = jobs.get(job_id)

    if job is None:
        return jsonify({
            "error": "Job not found."
        }), 404

    return jsonify({
        "job": public_job(job)
    }), 200


# POST /jobs/match
# Basic semantic matching against all stored jobs.
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

    resume = resumes.get(resume_id.strip())

    if resume is None:
        return jsonify({
            "error": "Resume not found."
        }), 404

    if resume.get("embedding_model") != MODEL_NAME:
        return jsonify({
            "error": "Resume embedding model does not match."
        }), 400

    resume_embedding = resume.get("embedding", [])

    matches = []

    for job in jobs.values():
        if job.get("embedding_model") != resume.get("embedding_model"):
            continue

        job_embedding = job.get("embedding", [])

        if len(resume_embedding) != len(job_embedding):
            continue

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

    matches.sort(
        key=lambda match: match["similarity_score"],
        reverse=True,
    )

    return jsonify({
        "resume_id": resume["id"],
        "total_matches": len(matches),
        "matches": matches
    }), 200


# POST /jobs/match-requirements
# Compare one resume against one job's individual requirements.
@jobs_bp.route("/match-requirements", methods=["POST"])
def match_requirements():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    resume_id = data.get("resume_id")
    job_id = data.get("job_id")

    if not isinstance(resume_id, str) or not resume_id.strip():
        return jsonify({
            "error": "A non-empty resume_id is required."
        }), 400

    if not isinstance(job_id, str) or not job_id.strip():
        return jsonify({
            "error": "A non-empty job_id is required."
        }), 400

    resume = resumes.get(resume_id.strip())

    if resume is None:
        return jsonify({
            "error": "Resume not found."
        }), 404

    job = jobs.get(job_id.strip())

    if job is None:
        return jsonify({
            "error": "Job not found."
        }), 404

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


# POST /jobs/hybrid-match
# Compare one resume against ALL stored jobs.
@jobs_bp.route("/hybrid-match", methods=["POST"])
def hybrid_match():
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

    resume = resumes.get(resume_id.strip())

    if resume is None:
        return jsonify({
            "error": "Resume not found."
        }), 404

    if not resume.get("analysis") or not resume.get("embedding"):
        return jsonify({
            "error": "Resume analysis or embedding is unavailable."
        }), 400

    if resume.get("embedding_model") != MODEL_NAME:
        return jsonify({
            "error": "Resume embedding model does not match."
        }), 400

    # First, rank all compatible jobs using hybrid matching.
    matches = calculate_hybrid_matches(resume, jobs)

    # Then, rerank those results using the Cross-Encoder.
    matches = rerank_with_cross_encoder(
        resume,
        matches,
        jobs,
    )

    return jsonify({
        "resume_id": resume["id"],
        "total_matches": len(matches),
        "ranking_method": {
            "name": "Hybrid NLP Matching with Cross-Encoder Reranking",
            "weights": {
                "semantic": SEMANTIC_WEIGHT,
                "bm25": BM25_WEIGHT,
                "structured": STRUCTURED_WEIGHT,
            },
            "final_ranking": "cross_encoder",
        },
        "matches": matches,
    }), 200


# POST /jobs/compare
# Compare one resume against ONE selected job.
@jobs_bp.route("/compare", methods=["POST"])
def compare_resume_to_job():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    resume_id = data.get("resume_id")
    job_id = data.get("job_id")

    if not isinstance(resume_id, str) or not resume_id.strip():
        return jsonify({
            "error": "A non-empty resume_id is required."
        }), 400

    if not isinstance(job_id, str) or not job_id.strip():
        return jsonify({
            "error": "A non-empty job_id is required."
        }), 400

    # Retrieve the selected resume.
    resume = resumes.get(resume_id.strip())

    if resume is None:
        return jsonify({
            "error": "Resume not found."
        }), 404

    # Retrieve the selected job.
    job = jobs.get(job_id.strip())

    if job is None:
        return jsonify({
            "error": "Job not found."
        }), 404

    # Verify that both documents have been analyzed.
    if not resume.get("analysis") or not job.get("analysis"):
        return jsonify({
            "error": "Resume or job analysis is unavailable."
        }), 400

    # Verify that both documents have compatible embeddings.
    if resume.get("embedding_model") != job.get("embedding_model"):
        return jsonify({
            "error": "Resume and job use different embedding models."
        }), 400

    if len(resume.get("embedding", [])) != len(job.get("embedding", [])):
        return jsonify({
            "error": "Resume and job embedding dimensions do not match."
        }), 400

    # Perform the detailed one-to-one evaluation.
    result = evaluate_resume_job(resume, job)

    return jsonify({
        "resume_id": resume["id"],
        "job": {
            "id": job["id"],
            "title": job["title"],
        },
        "evaluation_method": {
            "name": "Single Resume-to-Job Evaluation",
            "components": [
                "Semantic Similarity",
                "Structured Requirement Matching",
                "Cross-Encoder Relevance",
            ],
        },
        "evaluation": result,
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