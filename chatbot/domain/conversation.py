from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from users.domain.user_id import UserId
from chatbot.domain.message import Message


class ConversationStatus(Enum):
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"


@dataclass
class ConversationId:
    id: int


@dataclass
class Conversation:
    id: ConversationId
    user_id: UserId
    history: list[Message] = field(default_factory=list)
    status: ConversationStatus = ConversationStatus.ACTIVA
    created_at: datetime | None = None
    modified_at: datetime | None = None

    def add_message(self, message: Message) -> None:
        self.history.append(message)
        self.modified_at = datetime.now()

    def close(self) -> None:
        self.status = ConversationStatus.CERRADA
        self.modified_at = datetime.now()
