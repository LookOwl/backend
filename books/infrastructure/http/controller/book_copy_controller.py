from fastapi import APIRouter, Depends, HTTPException
from books.application.use_cases.delete_book_copy import DeleteBookCopy
from books.application.use_cases.update_book_copy import UpdateBookCopy
from books.infrastructure.di import get_deleter_book_copy_uc, get_updater_book_copies_uc
from books.infrastructure.http.dtos.update_book_copy_dto import UpdateBookCopyStatusDTO
from shared.infrastructure.di import jwt_auth_guard
from users.domain.user import User
from users.domain.user_role import UserRole

router = APIRouter(prefix="/book-copies", tags=["book-copies"])

@router.patch("/{copy_id}")
async def update_book_copy_status(
    copy_id: str,
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
            copy_id,
            user.id.uid,
            info.status
        )
    except Exception as exc:
        raise HTTPException(
            status_code=409,
            detail=f"No se pudo actualizar el estado de la copia, {exc} "
        )

@router.delete("/{copy_id}")
async def delete_book_copy(
    copy_id: str,
    user: User = Depends(jwt_auth_guard),
    delete_book_copy: DeleteBookCopy = Depends(get_deleter_book_copy_uc)
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code=403,
            detail="Solo bibliotecarios autorizados"
        )

    try:
        await delete_book_copy.execute(
            copy_id,
            user.id.uid
        )
    except Exception as exc:
        raise HTTPException(
            status_code=409,
            detail=f"No se pudo eliminar la copia, {exc} "
        )
