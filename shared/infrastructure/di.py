from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from users.domain.auth_guard import AuthGuard
from users.domain.token import EncryptedToken
from users.infrastructure.di import get_sql_user_repo
from shared.infrastructure.adapters.jwt_auth_guard import JWTAuthGuard
from users.application.ports import TokenHandler
from users.domain.user_repository import UserRepository
from users.infrastructure.di import get_jwt_token_handler


BEARER = HTTPBearer()


def get_jwt_auth_guard(
    token_handler : TokenHandler = Depends(get_jwt_token_handler),
    user_repo : UserRepository = Depends(get_sql_user_repo)
):
    return JWTAuthGuard(
        token_handler,user_repo
    )

async def jwt_auth_guard(
    credentials : HTTPAuthorizationCredentials = Security(BEARER),
    guard : AuthGuard = Depends(get_jwt_auth_guard)
):
    try:
        user =  await guard.resolve_token(EncryptedToken(credentials.credentials))
        return user
    except Exception:
        raise HTTPException(
            status_code=401,    #Unauthorized
            detail="Invalid token or user"
        )