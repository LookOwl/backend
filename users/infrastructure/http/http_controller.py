from fastapi import APIRouter, Depends, HTTPException
from shared.infrastructure.di import jwt_auth_guard
from users.application.delete_notification import DeleteNotificationsUseCase
from users.application.use_cases.get_notifications import GetNotificationsUseCase
from users.application.use_cases.register_user import RegisterUser
from users.domain.token import EncryptedToken

from users.application.use_cases.login_user import LoginUser
from users.domain.user import User
from users.infrastructure.di import get_delete_notification_use_case, get_login_user_uc, get_notifications_use_case, get_register_user_uc
from users.infrastructure.http.dtos.login_dto import LoginDto
from users.infrastructure.http.dtos.notification_dto import NotificationDto
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
            registerDto.password,
            registerDto.role
        )
    except Exception as e:
        print(e.__str__())
        raise HTTPException(
            422,
            detail="unsuccessful register"
        )
    
@router.get("/notifications")
async def get_loan_req_notifications(
    user : User = Depends(jwt_auth_guard),
    use_case : GetNotificationsUseCase = Depends(get_notifications_use_case)
):
    try:
        notifications = await use_case.execute(user.id.uid)
        return [
            NotificationDto(
                id = notification.notification_id.id,
                loan_req_id= notification.loan_req_id.id,
                notification_type=notification.type
            ) for notification in notifications
        ] 
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not available:{e.__str__()} "
        )

@router.delete("/notifications/{id}")
async def delete_loan_req_notification(
    id : int,
    user : User = Depends(jwt_auth_guard),
    use_case : DeleteNotificationsUseCase = Depends(get_delete_notification_use_case)
):
    try:
        await use_case.execute(user.id.uid)
        return
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not available:{e.__str__()} "
        )
