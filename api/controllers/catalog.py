from fastapi import APIRouter, Depends, HTTPException
from api.core.security import extract_user
from api.dtos.book_dto import RegisterBookDto
from api.services.book_service import BookService
from api.services.exports.di import get_book_service
from domain.user import User

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.post("/register")
async def registerBook(info : RegisterBookDto, user : User = Depends(extract_user), service : BookService = Depends(get_book_service)):
    if len(info.language) > 2: raise HTTPException(status_code=400, detail="Invalid language")
    id_created = await service.registerBook(info)
    print(f"user with id {user.uid} name {user.full_name} accessed the endpoint")
    return {
        "id" : id_created
    }
