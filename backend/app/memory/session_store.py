from typing import Dict, Optional
from app.ai.intent_schema import IntentModel


class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.last_intent: Optional[IntentModel] = None

    def update(self, intent: IntentModel):
        self.last_intent = intent

    def get_last_intent(self) -> Optional[IntentModel]:
        return self.last_intent


class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}

    def get_or_create(self, session_id: str) -> ConversationSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id)
        return self._sessions[session_id]

    def clear(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


# Singleton — imported and shared across the app
session_store = SessionStore()