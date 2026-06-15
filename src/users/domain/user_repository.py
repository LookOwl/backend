from abc import ABC, abstractmethod
from typing import Coroutine 
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_credential import UserCredentials

class UserRepository:
    
    @abstractmethod
    async def get_by_id(id : UserId) -> User | None:
        pass

    @abstractmethod
    async def get_by_email( email : str )-> User | None:
        pass
    
    @abstractmethod
    async def find_user_credential( email : str ) -> UserCredentials | None:
        pass

    @abstractmethod
    async def save_user( new_user : User) -> None:
        pass

    @abstractmethod
    async def delete_user( id : UserId ) -> None:
        pass

    @abstractmethod
    async def update_user( user : User ) -> None:
        pass