import uuid
from datetime import datetime
from dataclasses import dataclass, field

from app.models.schemas import ChatMessage
from app.core.exceptions import SessionNotFoundError


@dataclass
class Session:
    """Represents a single document Q&A session."""
    session_id: str
    filename: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    history: list[ChatMessage] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.history.append(ChatMessage(role=role, content=content))

    def get_history_for_llm(self) -> list[dict]:
        """Format history as Anthropic API message list."""
        return [{"role": m.role, "content": m.content} for m in self.history]

    @property
    def message_count(self) -> int:
        return len(self.history)


class SessionManager:
    """
    In-memory session store.
    Manages lifecycle of all active Q&A sessions.
    """

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create_session(self, filename: str) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, filename=filename)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session '{session_id}' not found.")
        return session

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> list[Session]:
        return list(self._sessions.values())
