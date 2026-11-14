from dataclasses import dataclass
from datetime import datetime


@dataclass
class Memory:
    id: str
    user_id: str
    content: str
    category: str
    importance: int = 3
    created_at: datetime | None = None


@dataclass
class ConversationMessage:
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime | None = None