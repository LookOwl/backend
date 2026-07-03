from fastapi import APIRouter, Depends, HTTPException

from loans.application.use_cases.assign_copy_to_request import AssignBookCopyToLoanRequestUseCase, CopyNoAvailableException, CopyNoExistsException, InvalidLoanRequestException
from loans.domain.loan_request import LoanRequest
from loans.infrastructure.di import get_assign_book_copy_uc, get_priviledged_requests_uc, get_request_loan_uc
from loans.infrastructure.http.dtos.assign_book_dto import AssignBookDto
from loans.infrastructure.http.dtos.loan_request_dto import LoanRequestDto
from shared.infrastructure.di import jwt_auth_guard
from loans.application.use_cases.get_priviledged_requests import GetPriviledgedRequests
from loans.application.use_cases.request_loan import RequestLoan
from loans.infrastructure.http.dtos.request_loan_dto import RequestLoanDto
from users.domain.user import User
from users.domain.user_role import UserRole


router = APIRouter(prefix="/request",tags=["request"])

#Ruta para obtener los préstamos asignables a un libro. Usable sólo por un bibliotecario
@router.get("/{book_id}")
async def getLoanRequests(
    book_id : int,
    get_requests_uc : GetPriviledgedRequests = Depends(get_priviledged_requests_uc), 
    user : User = Depends(jwt_auth_guard)
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code= 401,
            detail=f"Rol no autorizado: {user.role}"
        )
    try:
        results : list[LoanRequest] = await get_requests_uc.execute(book_id)
        return [ 
            LoanRequestDto.to_dto(result) for result in results 
        ]
    
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Service not available"
        )
    
#Ruta para alterar (asignar una copia física a una) solicitud de préstamo

@router.post("/assign")
async def assignBookCopyToRequest(
    body : AssignBookDto,
    user : User  = Depends(jwt_auth_guard),
    use_case : AssignBookCopyToLoanRequestUseCase = Depends(get_assign_book_copy_uc)
): 
    if(user.role != UserRole.BIBLIOTECARIO): 
        raise HTTPException(
            status_code=401,
            detail="Role not valid"
        )
    try:

        await use_case.execute(body.req_id,body.book_copy_code)
    
    except InvalidLoanRequestException:
        raise HTTPException(
            status_code=422,
            detail="Invalid LoanRequest"
        )
    except CopyNoExistsException:
        raise HTTPException(
            status_code=422,
            detail="Book copy does not exists"
        )
    except CopyNoAvailableException:
        raise HTTPException(
            status_code=409,
            detail="Copy is not available"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fatal error: {e.__str__()} "
        )

#Ruta para emitir una nueva solicitud de préstamo. Usable por todo usuario autenticado
@router.post("/")
async def requestLoan(
    loan_dto : RequestLoanDto, 
    user : User = Depends(jwt_auth_guard),
    request_loan_uc : RequestLoan = Depends(get_request_loan_uc)
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