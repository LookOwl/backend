from fastapi import APIRouter, Depends, HTTPException

from books.application.use_cases.update_book_copy import UpdateBookCopy
from books.infrastructure.di import get_updater_book_copies_uc
from books.infrastructure.http.dtos.update_book_copy_dto import UpdateBookCopyStatusDTO
from shared.infrastructure.di import jwt_auth_guard
from users.domain.user import User
from users.domain.user_role import UserRole

router = APIRouter(prefix="/book-copies", tags=["book-copies"])

@router.patch("{copy_id}")
async def update_book_copy_status(
    info: UpdateBookCopyStatusDTO,
    user: User = Depends(jwt_auth_guard),
    update_book_copy: UpdateBookCopy = Depends(get_updater_book_copies_uc)
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code=403,
            detail="Solo bibliotecarios autorizados"
        )

    try:
        await update_book_copy.execute(
            info.copy_id,
            user.id.uid,
            info.status
        )
    except Exception as exc:
        raise HTTPException(
            status_code=409,
            detail=f"No se pudo actualizar el estado de la copia, {exc} "
        )
