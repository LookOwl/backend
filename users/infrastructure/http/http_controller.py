from fastapi import APIRouter, Depends, HTTPException
from users.application.use_cases.register_user import RegisterUser
from users.domain.token import EncryptedToken

from users.application.use_cases.login_user import LoginUser
from users.infrastructure.di import get_login_user_uc, get_register_user_uc
from users.infrastructure.http.dtos.login_dto import LoginDto
from users.infrastructure.http.dtos.register_user_dto import RegisterUserDto


router = APIRouter(prefix="/users",tags=["users"])

@router.post("/login")
async def login(
    loginDto : LoginDto,
    login_use_case : LoginUser = Depends(get_login_user_uc),
):
    try:
        token : EncryptedToken = await login_use_case.execute(
            loginDto.email
            ,loginDto.password
        )
        res : dict[str, str] =  {
            "access_token" : token.raw_value,
            "token_type" : "bearer"
        }
        return res
    except Exception as e:
        print(e.__str__())
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    

@router.post("/register")
async def register(
    registerDto : RegisterUserDto, 
    register_use_case : RegisterUser =  Depends(get_register_user_uc)
):
    try:
        await register_use_case.execute(
            registerDto.fullname,
            registerDto.contact_number,
            registerDto.email,
            registerDto.password
        )
    except Exception as e:
        print(e.__str__())
        raise HTTPException(
            422,
            detail="unsuccessful register"
        )


