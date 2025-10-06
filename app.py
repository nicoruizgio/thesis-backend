from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from openai import OpenAI

# Load .env only outside production
if os.environ.get("FLASK_ENV") != "production":
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"Loading local .env at: {env_path}")
    load_dotenv(dotenv_path=env_path, verbose=False)

print(f"API key found: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")

try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    sys.exit(1)

# Global in‑memory state
transcript_cache = {}
user_info = {}
article_data = {}

def get_metadata(video_id):
    try:
        from pytube import YouTube
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(url)
        return {
            "title": yt.title,
            "author_name": yt.author,
            "thumbnail_url": yt.thumbnail_url,
            "length": yt.length,
        }
    except Exception as e:
        print(f"Metadata fetch error: {e}")
        return {}

app = Flask(__name__)

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
origin_list = [o.strip() for o in allowed_origins.split(",")] if allowed_origins else ["*"]
CORS(app, resources={r"/*": {"origins": origin_list}}, supports_credentials=False)

# FIX: use absolute (non-relative) imports since top-level dir has a hyphen
from routes.metadata import metadata_bp
from routes.transcript import transcript_bp
from routes.chat import chat_bp
from routes.user_info import user_info_bp
from routes.news_article import news_article_bp
from routes.generate_greeting import greeting_bp
from routes.auth import auth_bp

app.register_blueprint(metadata_bp)
app.register_blueprint(transcript_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(user_info_bp)
app.register_blueprint(news_article_bp)
app.register_blueprint(greeting_bp)
app.register_blueprint(auth_bp)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("FLASK_ENV") != "production")