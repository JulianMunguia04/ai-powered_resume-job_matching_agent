# Routes for /api

from flask import Blueprint

from .jobs import jobs_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(jobs_bp, url_prefix='/jobs')

