from flask import Blueprint, request, jsonify

greeting_bp = Blueprint("greeting_bp", __name__, url_prefix="/api")

@greeting_bp.route("/generate-greeting", methods=["POST"])
def generate_greeting():
    # defer app import to break circular dependency
    import backend.app as app

    try:
        data = request.json or {}
        ctype = data.get("type", "video")

        if not app.user_info:
            default = (f"Hi! How can I help you with this {ctype}?"
                       if ctype=="video" else f"Hi! How can I help you with this article?")
            return jsonify({"greeting": default})

        ui = app.user_info
        prompt = f"""Generate a brief, friendly greeting for a chatbot that helps users understand {'videos' if ctype=='video' else 'articles'}.

User information:
- Name: {ui.get('name','')}
- Origin/Country: {ui.get('origin','')}
- First language: {ui.get('language','')}

Requirements:
1. Start with "Hello" or "Hi" in the user's first language if possible
2. Address them by name if provided
3. End with "How can I help you with this {'video' if ctype=='video' else 'article'}?"
4. Keep it concise and welcoming
5. If you don't know how to say hello in their language, use English
6. Everything else apart from the greeting is in English

Generate the greeting now:"""

        resp = app.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}],
            max_tokens=100,
            temperature=0.7
        )
        return jsonify({"greeting": resp.choices[0].message.content.strip()})
    except Exception as e:
        print(f"Error generating greeting: {e}")
        default = "Hi! How can I help you with this video?"
        return jsonify({"greeting": default})