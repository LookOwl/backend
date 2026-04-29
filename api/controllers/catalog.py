from fastapi import APIRouter, Depends
from api.core.security import extract_user

from api.dtos.book_dto import RegisterBookDto

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.post("/register")
def registerBook(info : RegisterBookDto, user = Depends(extract_user)):
    return f"Book registered : {info.isbn}"

