from loans.application.ports import LoanRequestEventHandler
from shared.application.event_dispatcher import AppEventDispatcher
from shared.application.event_handler import EventHandler
from shared.domain.event_type import EventType


class LoanRequestEventDispatcher(AppEventDispatcher):

    suscribers : list[LoanRequestEventHandler]

    def __init__(self) -> None:
        super().__init__()
        self.suscribers = []

    async def notify(self, event : EventType) -> None:
        for suscriber in self.suscribers:
            await suscriber.handle(event)
        return

    async def suscribe(self, suscriber : EventHandler) -> None:
        if(isinstance(suscriber,LoanRequestEventHandler)):
            self.suscribers.append(suscriber)
        return

    async def detach(self, suscriber: EventHandler) -> None:
        if(isinstance(suscriber,LoanRequestEventHandler)):
            self.suscribers.remove(suscriber)
        return