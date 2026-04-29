from repositories.book_repository import BookRepository
from repositories.user_repository import UserRepository
from fastapi import Depends
from functools import lru_cache
from db.connection import get_db

@lru_cache()                #Esto es temporal, hasta que tenga una mejor alternativa (o base de datos)
def get_user_repository(
    db = None
):
    return UserRepository(db)

def get_book_repository(
    db = Depends(get_db)
):
    return BookRepository(db)
