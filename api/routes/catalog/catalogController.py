from fastapi import APIRouter

from api.dtos.bookDto import RegisterBookDto

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.post("/register")
def registerBook(info : RegisterBookDto):
    return f"Book registered : {info.isbn}"

