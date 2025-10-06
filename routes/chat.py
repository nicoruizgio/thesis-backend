from flask import Blueprint, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from prompts import system_prompt_video, system_prompt_article, search_agent_prompt
from collections import defaultdict
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
import os

chat_bp = Blueprint("chat_bp", __name__, url_prefix="/api")

TAVILY_KEY = os.environ.get("TAVILY_API_KEY")
_tools = []
if TAVILY_KEY:
    try:
        from langchain_tavily import TavilySearch
        tavily = TavilySearch(max_results=5, include_answer=True)
        _tools = [tavily]
    except Exception as e:
        print(f"Disable Tavily tool (init error): {e}")
else:
    print("Tavily tool disabled: TAVILY_API_KEY not set")

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

_AGENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", search_agent_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)
_agent = create_tool_calling_agent(_llm, _tools, _AGENT_PROMPT)

_memories = defaultdict(lambda: ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
))

@chat_bp.route("/chat", methods=["POST"])
def chat():
    import app as app
    data = request.json or {}
    user_message = data.get("message", "")
    content_type = data.get("type", "video")
    video_id = data.get("video_id", "")
    article_data = data.get("article", {})
    participant_id = data.get("participant_id") or "anonymous"
    memory = _memories[participant_id]

    try:
        if content_type == "article":
            if article_data:
                title = article_data.get("title", "") or ""
                authors = ", ".join(article_data.get("authors", [])) if isinstance(article_data.get("authors", []), list) else (article_data.get("authors") or "Unknown author")
                article_body = article_data.get("text", "") or ""
                meta_line = f"TITLE: {title}\nAUTHORS: {authors}\n"
                article_text = f"{meta_line}\n{article_body}"
            else:
                article_text = ""
                if app.article_data:
                    title = app.article_data.get("title", "") or ""
                    authors = ", ".join(app.article_data.get("authors", [])) or "Unknown author"
                    article_body = app.article_data.get("text", "") or ""
                    meta_line = f"TITLE: {title}\nAUTHORS: {authors}\n"
                    article_text = f"{meta_line}\n{article_body}"

            user_ctx = ""
            if app.user_info:
                user_ctx = "USER INFO:\n" + "\n".join(f"- {k}: {v}" for k, v in app.user_info.items() if v) + "\n"

            user_input = (
                f"{user_ctx}ARTICLE:\n{article_text or 'NO ARTICLE CONTENT AVAILABLE'}\n\n"
                f"USER QUESTION:\n{user_message}"
            )

            executor = AgentExecutor(agent=_agent, tools=_tools, verbose=True, memory=memory)
            result = executor.invoke({"input": user_input})
            reply = result.get("output", "").strip() or "Sorry, I could not generate an answer."
        else:
            system_message = system_prompt_video
            meta = app.get_metadata(video_id)
            if meta:
                system_message += f"\n\nVideo information: '{meta.get('title','')}' by {meta.get('author_name','')}"
            transcript = app.transcript_cache.get(video_id)
            if not transcript:
                try:
                    segs = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
                    transcript = ' '.join(s['text'] for s in segs)
                    app.transcript_cache[video_id] = transcript
                except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
                    transcript = ""
            system_message += f"\n\nTranscript: {transcript or 'No transcript available.'}"

            history_text = ""
            for m in memory.chat_memory.messages:
                role = "User" if m.type == "human" else "Assistant"
                history_text += f"{role}: {m.content}\n"

            composed = f"{system_message}\n\nConversation so far:\n{history_text}\nUser: {user_message}"

            executor = AgentExecutor(agent=_agent, tools=_tools, verbose=True, memory=memory)
            result = executor.invoke({"input": composed})
            reply = result.get("output", "").strip() or "Sorry, I could not generate an answer."

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500