from flask import Blueprint, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

transcript_bp = Blueprint("transcript_bp", __name__, url_prefix="/api")

@transcript_bp.route("/transcript/<video_id>")
def get_transcript(video_id):
    # defer your cache import too
    from backend.app import transcript_cache

    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        text = " ".join(s["text"] for s in segments)
        transcript_cache[video_id] = text
        return jsonify({"segments": segments, "text": text})
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        print(f"Transcript error: {e}")
        return jsonify({"segments": [], "text": ""})
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"segments": [], "text": ""}), 500