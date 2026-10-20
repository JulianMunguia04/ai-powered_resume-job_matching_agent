# Routes for /jobs

from uuid import uuid4

from flask import Blueprint, render_template, jsonify, request, abort

jobs_bp = Blueprint('jobs', __name__)

# Temporary in-memory-storage (Records disappear when server restarts)
jobs = {}

# GET /jobs Returns all jobs
@jobs_bp.route('/', methods=['GET'])
def get_all_jobs():
  return jsonify({"jobs": list(jobs.values())}), 200

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

  job = {
      "id": str(uuid4()),
      "title": title.strip(),
      "description": description.strip()
  }

  jobs[job["id"]] = job

  return jsonify({"job": job}), 201

# /jobs/[job_id] get job by id
@jobs_bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    """Return one job by its ID."""
    job = jobs.get(job_id)

    if job is None:
        return jsonify({
            "error": "Job not found."
        }), 404

    return jsonify({"job": job}), 200