# chat_history = []

# def add_message(role, content):
#     chat_history.append({
#         "role": role,
#         "content": content
#     })

# def get_history(limit=6):
#     return chat_history[-limit:]

"""
Per-session chat memory. Previously a single global list shared
by every user — now keyed by session_id so different users/tabs
don't see each other's conversations.

This is in-memory (dies on server restart). Fine for a demo/portfolio
project. For real persistence, swap the dict for Redis or SQLite.
"""

from app.logger import get_logger

logger = get_logger(__name__)

_sessions: dict[str, list[dict]] = {}


def add_message(session_id: str, role: str, content: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})


def get_history(session_id: str, limit: int = 6) -> list[dict]:
    return _sessions.get(session_id, [])[-limit:]


def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    logger.info(f"Cleared session {session_id}")