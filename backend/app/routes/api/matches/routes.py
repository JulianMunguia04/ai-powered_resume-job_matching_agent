
from flask import Blueprint, jsonify

matches_bp = Blueprint("matches", __name__)


@matches_bp.route("/", methods=["GET"])
def get_matches():
    """
    Retrieve generated resume-job matches.

    Matching functionality will be implemented later.
    """

    return jsonify({
        "success": True,
        "total": 0,
        "matches": []
    }), 200
