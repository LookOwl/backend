from abc import ABC, abstractmethod
from users.domain.token import EncryptedToken
from users.domain.user import User


class AuthGuard(ABC):

    @abstractmethod
    async def resolve_token(self,encrypted_token : EncryptedToken) -> User:
        pass