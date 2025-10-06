from flask import Blueprint, jsonify

metadata_bp = Blueprint("metadata_bp", __name__, url_prefix="/api")

@metadata_bp.route("/metadata/<video_id>")
def get_video_metadata(video_id):
    from app import get_metadata  # changed
    try:
        data = get_metadata(video_id)
        return jsonify(data)
    except Exception as e:
        print(f"Metadata error: {e}")
        return jsonify({}), 500