from fastapi import Depends
from api.services.auth_service import AuthService
from repositories.exports.di import get_user_repository

def get_auth_service(
    user_repo = Depends(get_user_repository)
):
    return AuthService(user_repo)
