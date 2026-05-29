from fastapi import APIRouter, Depends, HTTPException
from api.dtos.loan_dto import UpdateLoanDto

from services.loan_service import LoanService, LoanException
from dependencies.services import get_loan_service

from domain.user import User
from domain.enums.roles_usuario import RolUsuario
from core.security import extract_user

router = APIRouter(prefix="/loans",tags=["loans"])

@router.get("/loans")
async def getLoans(limit:int = 20,offset:int = 0,loanService : LoanService = Depends(get_loan_service), user:User = Depends(extract_user)):
    if user.role != RolUsuario.BIBLIOTECARIO:
        raise HTTPException(
            status_code= 401,
            detail=f"Rol no autorizado: {user.role}"
        )
    try:
        result = await loanService.get_loans(limit,offset)
        return list(result)
    except LoanException:
        raise HTTPException(
            status_code=503,
            detail="Service not available"
        )

@router.post(path="/register")
async def updateLoanStatus( loan: UpdateLoanDto, user : User = Depends(extract_user), loanService: LoanService = Depends(get_loan_service) ):
    if user.role != RolUsuario.BIBLIOTECARIO:
        raise HTTPException(
            status_code= 401,
            detail=f"Rol no autorizado: {user.role}"
        )
    try:
        ok = await loanService.updateLoanStatus(loan, user)
    except LoanException:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable loan update"
        )
    return {
        "loan_updated" : ok
    }


