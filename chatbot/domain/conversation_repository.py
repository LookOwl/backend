from abc import ABC, abstractmethod
from users.domain.user_id import UserId
from chatbot.domain.conversation import Conversation


class ConversationRepository(ABC):

    @abstractmethod
    async def load(self, user_id: UserId) -> Conversation | None:
        pass

    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        pass
