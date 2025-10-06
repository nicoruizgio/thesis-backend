from flask import Blueprint, request, jsonify

user_info_bp = Blueprint("user_info_bp", __name__, url_prefix="/api")

@user_info_bp.route("/user-info", methods=["POST"])
def save_user_info():
    import app as app

    try:
        data = request.json or {}

        # Store user info in the global variable
        app.user_info = data

        print(f"User info saved: {data}")

        return jsonify({
            "message": "User information saved successfully",
            "data": data
        }), 200

    except Exception as e:
        print(f"Error saving user info: {e}")
        return jsonify({
            "error": "Failed to save user information"
        }), 500