from abc import ABC, abstractmethod
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_credential import UserCredentials
from users.domain.user_notification import UserNotification

class UserRepository(ABC):
    
    @abstractmethod
    async def get_by_id(self,id : UserId) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email : str )-> User | None:
        pass
    
    @abstractmethod
    async def get_notifications(self, user_id : UserId) -> list[UserNotification]:
        pass

    @abstractmethod
    async def post_notification(self, notification : UserNotification) -> None:
        pass

    @abstractmethod
    async def find_user_credential(self, email : str ) -> UserCredentials | None:
        pass

    @abstractmethod
    async def save_user( self, new_user : User) -> None:
        pass

    @abstractmethod
    async def delete_user( self, id : UserId ) -> None:
        pass

    @abstractmethod
    async def update_user( self, user : User ) -> None:
        pass