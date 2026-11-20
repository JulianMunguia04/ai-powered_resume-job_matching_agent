
from uuid import UUID

from flask import Blueprint, jsonify, request, current_app

from services.database import db
from services.matching_service import (
    find_jobs_for_resume,
    find_applicants_for_job,
)

from models import Matching


matches_bp = Blueprint("matches", __name__)


def parse_uuid(value):
    try:
        return UUID(value)
    except (ValueError, TypeError, AttributeError):
        return None


def get_top_k_from_request():
    value = request.args.get("limit", 10)

    try:
        value = int(value)
    except (ValueError, TypeError):
        value = 10

    return max(1, min(value, 50))


# --------------------------------------------------
# GET /api/matches/
# Retrieve saved resume-job matches.
# --------------------------------------------------

@matches_bp.route("/", methods=["GET"])
def get_matches():
    try:
        matches = Matching.query.order_by(
            Matching.created_at.desc()
        ).all()

        return jsonify({
            "success": True,
            "total": len(matches),
            "matches": [
                {
                    "id": str(match.id),
                    "resume_id": str(match.resume_id),
                    "job_id": str(match.job_id),
                    "text": match.text,
                    "analysis": match.analysis,
                    "scores": match.scores,
                    "created_at": match.created_at.isoformat(),
                    "updated_at": match.updated_at.isoformat(),
                }
                for match in matches
            ],
        }), 200

    except Exception as error:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to retrieve saved matches"
        )

        return jsonify({
            "error": "Failed to retrieve matches.",
            "details": str(error),
        }), 500


# --------------------------------------------------
# GET /api/matches/resumes/<resume_id>
# Find top matching jobs for one resume.
# --------------------------------------------------

@matches_bp.route(
    "/resumes/<resume_id>",
    methods=["GET"],
)
def get_jobs_for_resume(resume_id):
    parsed_id = parse_uuid(resume_id)

    if parsed_id is None:
        return jsonify({
            "error": "Invalid resume ID."
        }), 400

    try:
        result = find_jobs_for_resume(
            resume_id=parsed_id,
            top_k=get_top_k_from_request(),
        )

        return jsonify({
            "success": True,
            **result,
        }), 200

    except LookupError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to find matching jobs for resume %s",
            parsed_id
        )

        return jsonify({
            "error": "Failed to find matching jobs.",
            "details": str(error),
        }), 500


# --------------------------------------------------
# GET /api/matches/jobs/<job_id>
# Find top matching applicants for one job.
# --------------------------------------------------

@matches_bp.route(
    "/jobs/<job_id>",
    methods=["GET"],
)
def get_applicants_for_job(job_id):
    parsed_id = parse_uuid(job_id)

    if parsed_id is None:
        return jsonify({
            "error": "Invalid job ID."
        }), 400

    try:
        result = find_applicants_for_job(
            job_id=parsed_id,
            top_k=get_top_k_from_request(),
        )

        return jsonify({
            "success": True,
            **result,
        }), 200

    except LookupError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to find matching applicants for job %s",
            parsed_id
        )

        return jsonify({
            "error": "Failed to find matching applicants.",
            "details": str(error),
        }), 500


# --------------------------------------------------
# GET /api/matches/<matching_id>
# Retrieve one saved match.
# --------------------------------------------------

@matches_bp.route(
    "/<matching_id>",
    methods=["GET"],
)
def get_matching(matching_id):
    parsed_id = parse_uuid(matching_id)

    if parsed_id is None:
        return jsonify({
            "error": "Invalid matching ID."
        }), 400

    try:
        matching = db.session.get(Matching, parsed_id)

        if matching is None:
            return jsonify({
                "error": "Matching not found."
            }), 404

        return jsonify({
            "success": True,
            "matching": {
                "id": str(matching.id),
                "resume_id": str(matching.resume_id),
                "job_id": str(matching.job_id),
                "text": matching.text,
                "analysis": matching.analysis,
                "scores": matching.scores,
                "created_at": matching.created_at.isoformat(),
                "updated_at": matching.updated_at.isoformat(),
            },
        }), 200

    except Exception as error:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to retrieve matching record %s",
            parsed_id
        )

        return jsonify({
            "error": "Failed to retrieve matching record.",
            "details": str(error),
        }), 500
