from loans.application.loan_event_handler import LoanEventHandler
from shared.application.event_dispatcher import AppEventDispatcher
from shared.application.event_handler import EventHandler
from shared.domain.event_type import EventType


class LoanEventDispatcher(AppEventDispatcher):

    suscribers : list[LoanEventHandler]

    def __init__(self) -> None:
        super().__init__()
        self.suscribers = []

    async def suscribe(self, suscriber: EventHandler) -> None:
        assert isinstance(suscriber,LoanEventHandler)
        self.suscribers.append(suscriber)
        return

    async def notify(self, event: EventType) -> None:
        for suscriber in self.suscribers:
            await suscriber.handle(event)
        return

    async def detach(self, suscriber: EventHandler) -> None:
        assert isinstance(suscriber,LoanEventHandler)
        self.suscribers.remove(suscriber)
        return