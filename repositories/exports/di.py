from api.repositories.user_repository import UserRepository
from fastapi import Depends
from functools import lru_cache

@lru_cache()                #Esto es temporal, hasta que tenga una mejor alternativa (o base de datos)
def get_user_repository(
    db = None
):
    return UserRepository(db)