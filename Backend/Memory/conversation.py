
from collections import defaultdict

conversation_history = defaultdict(list)


def get_conversation_history(session_id: str):
    """Return recent messages for a session."""
    if not session_id.strip():
        return []

    return list(conversation_history.get(session_id, []))


def add_message(session_id: str, role: str, content: str):
    """Save a message for a specific session."""

    if not session_id.strip():
        raise ValueError("Session ID cannot be empty.")

    if role not in {"user", "assistant"}:
        raise ValueError("Role must be user or assistant.")

    if not content.strip():
        return

    conversation_history[session_id].append({
        "role": role,
        "content": content
    })

    # Keep the latest 10 messages
    conversation_history[session_id] = (
        conversation_history[session_id][-10:]
    )


def clear_conversation(session_id: str):
    """Clear history for one session."""
    conversation_history.pop(session_id, None)


def clear_all_conversations():
    """Clear all in-memory conversation history."""
    conversation_history.clear()
