


from shared.application.unit_of_work import UnitOfWork
from users.domain.user_notification import NotificationId
from users.domain.user_repository import UserRepository


class DeleteNotificationsUseCase:

    uow : UnitOfWork
    user_repo : UserRepository

    def __init__(
            self,
            uow : UnitOfWork,
            user_repo : UserRepository
        ) -> None:
        self.uow =  uow
        self.user_repo =  user_repo

    async def execute(self, notification_id : int ):
        async with self.uow:
            await self.user_repo.delete_notification(NotificationId(notification_id))
        return