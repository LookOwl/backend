from fastapi import APIRouter, Depends, HTTPException

from books.infrastructure.http.http_controller import jwt_auth_guard
from loans.application.use_cases.get_priviledged_requests import GetPriviledgedRequests
from loans.application.use_cases.request_loan import RequestLoan
from loans.infrastructure.http.dtos.request_loan_dto import RequestLoanDto
from users.domain.user import User
from users.domain.user_role import UserRole


router = APIRouter(prefix="/loans",tags=["loans"])

@router.get("/{id}")
async def getLoans(
    id : int,
    limit:int = 20,
    offset:int = 0,
    get_requests_uc : GetPriviledgedRequests = Depends(), 
    user : User = Depends()
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code= 401,
            detail=f"Rol no autorizado: {user.role}"
        )
    try:
        result = await get_requests_uc.execute(id)
        return result
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Service not available"
        )

@router.post("/request")
async def requestLoan(
    loan_dto : RequestLoanDto, 
    user : User = Depends(jwt_auth_guard),
    request_loan_uc : RequestLoan = Depends()
):
    try:
        await request_loan_uc.execute(
            user.id.uid,
            loan_dto.book_id,
            loan_dto.interest_window,
            loan_dto.n_days_requested
        )

    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=f"Book cannot be borrowed: {e}"
        )
