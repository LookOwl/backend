from fastapi import APIRouter, Depends, HTTPException

from loans.application.use_cases.get_loans_by_book import GetLoansOfBookUseCase
from loans.application.use_cases.get_loans_by_user import GetLoansOfUserUseCase
from loans.application.use_cases.register_new_loan import CreateLoanUseCase, LoanRequestInconsistentStatus, LoanRequestNotFoundException
from loans.application.use_cases.return_book import LoanNotFoundException, ReturnBookUseCase
from loans.infrastructure.di import get_loans_of_book_uc, get_loans_of_user_uc, get_return_book_uc, get_start_loan_uc
from loans.infrastructure.http.dtos.create_loan_dto import CreateLoanDto
from loans.infrastructure.http.dtos.loan_dto import LoanDto
from loans.infrastructure.http.dtos.return_book_dto import ReturnBookDto
from shared.infrastructure.di import jwt_auth_guard
from users.domain.user import User
from users.domain.user_role import UserRole

router  = APIRouter(prefix="/loans",tags=["loans"])

'''
Endpoints:
- Registrar inicio de préstamo (bibliotecario)
- Consultar mis préstamos (por usuario)
- Consultar préstamos de un libro (bibliotecario)
- Registrar devolución de libro (bibliotecario)
'''
@router.post(path="/start")
async def start_loan( 
        body : CreateLoanDto,
        user : User = Depends(jwt_auth_guard),
        use_case : CreateLoanUseCase = Depends(get_start_loan_uc)  
):
    if(user.role != UserRole.BIBLIOTECARIO):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized : Only BIBLIOTECARIO role"
        )
    try:
        await use_case.execute(body.req_id)
    except LoanRequestNotFoundException:
        raise HTTPException(
            status_code=422,
            detail="Cannot found the loan request"
        )
    except LoanRequestInconsistentStatus:
        raise HTTPException(
            status_code=409,
            detail="Loan has already been started, or does not have a physical copy assigned"
        )
    except Exception as e:
        print(e.__str__())
        raise HTTPException(
            status_code=503,
            detail=f"Fatal error: {e.__str__()}"
        )
    

@router.get(path="/user")
async def get_loans_of_user(
    user : User = Depends(jwt_auth_guard),
    use_case : GetLoansOfUserUseCase = Depends(get_loans_of_user_uc)
):
    try:
        loans = await use_case.execute(user.id.uid)
        return [
            LoanDto(
                id = loan.id.id,
                user_id= loan.user_id.uid,
                book_copy_id= loan.book_copy_id.id ,
                book_id = loan.book_id.id,
                approval_date = loan.approval_date,
                due_date = loan.due_date,
                return_date = loan.return_date,
                status = loan.status
            ) for loan in loans
        ]
    except Exception as e:
        return HTTPException(
            status_code=503,
            detail=f"Cannot attend request: {e.__str__()}"
        )
    

@router.get(path="/{book_id}")
async def get_loans_of_book(
    book_id : int,
    user : User = Depends(jwt_auth_guard),
    use_case : GetLoansOfBookUseCase = Depends(get_loans_of_book_uc)
):
    if(user.role != UserRole.BIBLIOTECARIO):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized : Only BIBLIOTECARIO role"
        )

    try:
        loans = await use_case.execute(book_id)
        return [
            LoanDto(
                id = loan.id.id,
                user_id= loan.user_id.uid,
                book_copy_id= loan.book_copy_id.id ,
                book_id = loan.book_id.id,
                approval_date = loan.approval_date,
                due_date = loan.due_date,
                return_date = loan.return_date,
                status = loan.status
            ) for loan in loans
        ]
    except Exception as e:
        return HTTPException(
            status_code=503,
            detail=f"Cannot attend request: {e.__str__()}"
        )

@router.post("/return")
async def return_book(
    body : ReturnBookDto,
    user : User = Depends(jwt_auth_guard),
    use_case : ReturnBookUseCase = Depends(get_return_book_uc)
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized : Only BIBLIOTECARIO role"
        )
    try:
        await use_case.execute(body.book_physical_copy_code)
        return
    except LoanNotFoundException:
        raise HTTPException(
            status_code=422,
            detail="Loan not found"
        ) 
    except Exception as e:
        print(e.__str__())
        raise HTTPException(
            status_code=422,
            detail=f"Fatal error: {e.__str__()}"
        )
