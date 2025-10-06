from flask import Blueprint, request, jsonify
from datetime import datetime
import os

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api")

# Shared password (in production, use environment variable)
SHARED_PASSWORD = os.environ.get("SHARED_PASSWORD")
if os.environ.get("FLASK_ENV") == "production" and not SHARED_PASSWORD:
    raise RuntimeError("SHARED_PASSWORD not set in production environment")

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json or {}
        participant_id = data.get("participant_id", "").strip()
        password = data.get("password", "")

        # Validate inputs
        if not participant_id:
            return jsonify({"success": False, "error": "Participant code is required"}), 400

        # Check shared password
        if password != SHARED_PASSWORD:
            return jsonify({"success": False, "error": "Invalid password"}), 401

        # Return success with participant data
        return jsonify({
            "success": True,
            "data": {
                "participant_id": participant_id,
                "login_time": datetime.now().isoformat()
            }
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"success": False, "error": "Server error"}), 500