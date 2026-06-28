from abc import ABC, abstractmethod


"""Base class for all events"""
class EventType(ABC):
    
    @abstractmethod
    def get_type(self) -> type:
        pass