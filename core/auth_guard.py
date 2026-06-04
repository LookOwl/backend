from fastapi import Security, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependencies.services import get_auth_service, AuthService
import jwt

BEARER = HTTPBearer()

async def user_auth_guard(
    credentials: HTTPAuthorizationCredentials = Security(BEARER),
    auth_service : AuthService = Depends(get_auth_service)
):
    try:
        print(credentials)
        user = await auth_service.validateToken(credentials.credentials)
        print(user)
        if user is None:
            raise ValueError
        return user

    except (jwt.PyJWTError, ValueError) as e:
        print(e.__str__())
        raise HTTPException(
                status_code=401,    #Unauthorized
                detail="Invalid token or user"
            )

    except Exception as e:
        raise HTTPException(
            status_code=422,        #Unprocessable Entity
            detail=f"Fatal error. User id might not be an int: {e.__str__()}"
        )
