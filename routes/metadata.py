from flask import Blueprint, jsonify

metadata_bp = Blueprint("metadata_bp", __name__, url_prefix="/api")

@metadata_bp.route("/metadata/<video_id>")
def get_video_metadata(video_id):
    # defer import until runtime to break the circular dependency
    from backend.app import get_metadata

    try:
        data = get_metadata(video_id)
        return jsonify(data)
    except Exception as e:
        print(f"Metadata error: {e}")
        return jsonify({}), 500