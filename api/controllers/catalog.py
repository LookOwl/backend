from fastapi import APIRouter

from api.dtos.book_dto import RegisterBookDto

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.post("/register")
def registerBook(info : RegisterBookDto):
    return f"Book registered : {info.isbn}"

