from abc import ABC, abstractmethod
from shared.domain.event_type import EventType
from shared.application.event_handler import EventHandler

class AppEventDispatcher(ABC):

    @abstractmethod
    async def notify(self,event: EventType) -> None:
        pass
    
    @abstractmethod
    async def suscribe(self, suscriber : EventHandler) -> None:
        pass
    
    @abstractmethod
    async def detach(self, suscriber: EventHandler) -> None:
        pass
