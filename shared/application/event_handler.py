from abc import ABC , abstractmethod
from shared.domain.event_type import EventType


"""Base class for all application event handlers. 
Do not implement directly, instead, implement some of its subclasses"""
class EventHandler(ABC):
    
    @abstractmethod
    async def handle(self,event : EventType) -> None:
        pass

