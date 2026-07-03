from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from users.domain.auth_guard import AuthGuard
from users.domain.token import EncryptedToken
from users.infrastructure.adapters.sql_user_repository import SQLUserRepository
from shared.infrastructure.adapters.jwt_auth_guard import JWTAuthGuard
from users.application.ports import TokenHandler
from users.domain.user_repository import UserRepository
from users.infrastructure.di import get_jwt_token_handler
from shared.infrastructure.persistence.sql_drivers import async_session_factory


BEARER = HTTPBearer()

async def get_auth_async_sql_session():
    async with async_session_factory() as session:
        yield session

def get_auth_user_repo(
    session: AsyncSession = Depends(get_auth_async_sql_session)
):
    return SQLUserRepository(session)

def get_jwt_auth_guard(
    token_handler : TokenHandler = Depends(get_jwt_token_handler),
    user_repo : UserRepository = Depends(get_auth_user_repo)
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
    except Exception as e:
        print(e.__str__())
        raise HTTPException(
            status_code=401,    #Unauthorized
            detail="Invalid token or user"
        )
