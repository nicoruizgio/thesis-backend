from flask import Blueprint, request, jsonify
from newspaper import Article

news_article_bp = Blueprint("news_article_bp", __name__, url_prefix="/api")

@news_article_bp.route("/news-article", methods=["POST"])
def extract_news_article():
    import app as app  # changed

    try:
        url = (request.json or {}).get("url", "")
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        art = Article(url)
        art.download(); art.parse()

        app.article_data = {
            'title': art.title,
            'text': art.text,
            'authors': art.authors,
            'top_image': art.top_image,
            'publish_date': str(art.publish_date) if art.publish_date else None
        }
        return jsonify(app.article_data)
    except Exception as e:
        print(f"Error extracting article: {e}")
        return jsonify({'error': 'Failed to extract article'}), 500