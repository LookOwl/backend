


from shared.application.unit_of_work import UnitOfWork
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository


class GetNotificationsUseCase:

    uow : UnitOfWork
    user_repo : UserRepository

    def __init__(
            self,
            uow : UnitOfWork,
            user_repo : UserRepository
        ) -> None:
        self.uow =  uow
        self.user_repo =  user_repo

    async def execute(self, user_id : int):
        async with self.uow:
            notifications = await self.user_repo.get_notifications(UserId(user_id))
        return notifications