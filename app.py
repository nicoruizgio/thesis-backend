from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from openai import OpenAI

# Only load .env in local/dev (Render will supply real env vars)
if os.environ.get("FLASK_ENV") != "production":
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"Loading local .env at: {env_path}")
    load_dotenv(dotenv_path=env_path, verbose=True)

# Debug - print API key existence (don't print the actual key)
print(f"API key found: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")

# Initialize OpenAI client - catch error to debug
try:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    # Temporary fallback for testing
    sys.exit(1)  # Exit if no API key to prevent further errors

# --- Add these module‐level globals and helper before you import any blueprints ---
transcript_cache = {}
user_info      = {}
article_data   = {}

def get_metadata(video_id):
    """
    Fetch basic YouTube metadata. Requires pytube.
    Falls back to empty dict on error.
    """
    try:
        from pytube import YouTube
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt  = YouTube(url)
        return {
            "title":         yt.title,
            "author_name":   yt.author,
            "thumbnail_url": yt.thumbnail_url,
            "length":        yt.length,
        }
    except Exception as e:
        print(f"Metadata fetch error: {e}")
        return {}

app = Flask(__name__)

# Configure CORS with allowed origins from env (comma‑separated)
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
origin_list = [o.strip() for o in allowed_origins.split(",")] if allowed_origins else ["*"]
CORS(app, resources={r"/*": {"origins": origin_list}}, supports_credentials=False)

# import blueprints as a package
from .routes.metadata            import metadata_bp
from .routes.transcript          import transcript_bp
from .routes.chat                import chat_bp
from .routes.user_info           import user_info_bp
from .routes.news_article        import news_article_bp
from .routes.generate_greeting   import greeting_bp
from .routes.auth                import auth_bp  # Add this import

# register them
app.register_blueprint(metadata_bp)
app.register_blueprint(transcript_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(user_info_bp)
app.register_blueprint(news_article_bp)
app.register_blueprint(greeting_bp)
app.register_blueprint(auth_bp)  # Register the auth blueprint

# Simple health endpoint for uptime checks
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Use host 0.0.0.0 so Render can reach it; PORT from env (fallback 5000 locally)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_ENV") != "production")