# Routes for /jobs

from flask import Blueprint, render_template, jsonify, request, abort

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
def get_all_jobs():
  return "Jobs Route"

@jobs_bp.route('/', methods=['POST'])
def create_job():
  return "All Jobs"

@jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
  return f"job id: {job_id}"