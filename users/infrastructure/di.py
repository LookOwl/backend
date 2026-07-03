from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.infrastructure.persistence.di import get_sql_unit_of_work
from shared.application.unit_of_work import UnitOfWork
from shared.infrastructure.persistence.di import get_async_sql_session
from users.application.ports import PasswordHasher, TokenHandler
from users.application.use_cases.login_user import LoginUser
from users.application.use_cases.register_user import RegisterUser
from users.domain.user_repository import UserRepository
from users.infrastructure.adapters.bcrypt_hasher import BcryptPasswordHasher
from users.infrastructure.adapters.jwt_token_handler import JWTTokenHandler
from users.infrastructure.adapters.sql_user_repository import SQLUserRepository

def get_sql_user_repo(
    async_session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLUserRepository(async_session=async_session)

def get_bcrypt_password_hasher():
    return BcryptPasswordHasher()

def get_jwt_token_handler():
    return JWTTokenHandler()

def get_register_user_uc(
        user_repo : UserRepository = Depends(get_sql_user_repo),
        password_hasher : PasswordHasher = Depends(get_bcrypt_password_hasher),
        uow : UnitOfWork =Depends(get_sql_unit_of_work)
):
    return RegisterUser(
        user_repo=user_repo,
        password_hasher=password_hasher,
        uow = uow
    )

def get_login_user_uc(
    user_repo: UserRepository = Depends(get_sql_user_repo),
    hasher: PasswordHasher = Depends(get_bcrypt_password_hasher),
    token_handler: TokenHandler = Depends(get_jwt_token_handler),
    uow: UnitOfWork = Depends(get_sql_unit_of_work)
):
    return LoginUser(
        user_repo,
        hasher,
        token_handler,
        uow
    )