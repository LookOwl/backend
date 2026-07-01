from typing import Any

from shared.application.event_dispatcher import AppEventDispatcher
from shared.application.event_handler import EventHandler


class EventDispatcherFactory:

    @staticmethod
    async def create( 
        dispatcher_cls : type, 
        with_suscribers : dict[type, tuple[Any,...]],
        dispatcher_args : list[Any] = []
    ):
        #Assert polymorphism
        assert issubclass(dispatcher_cls,AppEventDispatcher)
        for suscriber_cls in with_suscribers:
            assert issubclass(suscriber_cls,EventHandler)
        
        #Create the event handler
        instance = dispatcher_cls(*dispatcher_args)
        for suscriber in with_suscribers.keys():
            await instance.suscribe(suscriber(*with_suscribers[suscriber]))
        
        return instance