from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from books.infrastructure.di import RedisController, RedisLockManager
from users.domain.auth_guard import AuthGuard
from users.domain.token import EncryptedToken
from users.infrastructure.di import get_sql_user_repo
from shared.infrastructure.adapters.jwt_auth_guard import JWTAuthGuard
from users.application.ports import TokenHandler
from users.domain.user_repository import UserRepository
from users.infrastructure.di import get_jwt_token_handler
from shared.infrastructure.persistence.sql_drivers import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

BEARER = HTTPBearer()

from shared.infrastructure.persistence.sql_unit_of_work import SQLUnitOfWork

async def get_redis_session(
    request : Request =  Depends(Request)
):
    assert isinstance(request.state.redis, Redis)
    return request.state.redis


async def get_redis_controller(
    redis : Redis = Depends(get_redis_session)       
):
    return RedisController(
        redis
    )

async def get_redis_lock_manager(
    redis : Redis = Depends(get_redis_session)
):
    return RedisLockManager(
        redis
    )

async def get_async_sql_session():
    async with async_session_factory() as session:
        yield session


async def get_sql_unit_of_work(
    session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLUnitOfWork(
        session
    )


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