from fastapi import APIRouter, Depends, HTTPException
from api.dtos.login_dto import LoginDto , RegisterUserDto
from services.auth_service import AuthService, UserAlreadyExistsException, UnknownException
from dependencies.services import get_auth_service

router = APIRouter(prefix="/users",tags=["users"])

@router.post("/login")
async def login(
    loginDto:LoginDto,
    authService : AuthService = Depends(get_auth_service),
):
    token = await authService.validateUser(loginDto.email,loginDto.password)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail = "User not found"
        )
    return {
        "access_token" : token,
        "token_type" : "bearer"
    }

@router.post("/register")
async def register(registerDto : RegisterUserDto, authService : AuthService = Depends(get_auth_service)):
    try:
        success = await authService.registerUser(registerDto)
        return {
            "user_id" : success.uid,
            "role" : success.role
        }
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=409,
            detail="El email ya está registrado"
        )
    except UnknownException as e:
        raise e #TODO(Quitar esto luego, sólo con propósitos de debug)
    
