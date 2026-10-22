from retrieval.search import search_chunks
from llm.gemini_client import generate_response
from llm.memory import get_history, add_message
from app.logger import get_logger

logger = get_logger(__name__)


def ask_rag(query: str, session_id: str = "default"):
    add_message(session_id, "user", query)

    chunks = search_chunks(query)
    history = get_history(session_id)

    conversation = ""
    for msg in history:
        conversation += f"{msg['role']}: {msg['content']}\n"

    answer = generate_response(query, chunks, conversation)
    add_message(session_id, "assistant", answer)

    return answer, chunks