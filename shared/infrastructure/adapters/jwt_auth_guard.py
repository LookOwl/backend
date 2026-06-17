
from users.application.ports import TokenHandler
from users.domain.auth_guard import AuthGuard
from users.domain.token import EncryptedToken, Token
from users.domain.user_repository import UserRepository


class JWTAuthGuard(AuthGuard):
    token_handler : TokenHandler
    user_repo : UserRepository

    def __init__(
            self,
            token_handler : TokenHandler,
            user_repo : UserRepository
        ) -> None:
        self.token_handler = token_handler 
        self.user_repo = user_repo

    async def resolve_token(self,encrypted_token : EncryptedToken):
        token : Token = self.token_handler.decrypt_token(encrypted_token)
        user = await self.user_repo.get_by_id(token.user_id)
        if not user or user.role != token.role:
            raise Exception("Unauthorized")
        return user