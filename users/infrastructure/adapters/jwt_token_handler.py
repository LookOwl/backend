from datetime import datetime, timezone, timedelta
from shared.infrastructure.settings import settings
from users.application.ports import TokenHandler
from users.domain.token import EncryptedToken, Token
from users.domain.user_id import UserId
from users.domain.user_role import UserRole
import jwt

class JWTTokenHandler(TokenHandler):
    
    def generate_token(self,user_id : UserId, user_role : UserRole ) -> EncryptedToken:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(
            minutes=settings.JWT_EXPIRE_TIME_IN_MINUTES
        )
        payload : dict[str,str | datetime | UserRole]  = {
            "sub" : str(user_id),
            "exp" : expire,
            "iat" : now,
            "iss" : "LookOwl-Server" ,
            "role" : user_role
        }

        return EncryptedToken(jwt.encode( #type: ignore
            payload = payload,
            key = settings.JWT_SECRET_KEY,
            algorithm = settings.JWT_ALGORITHM
        ))
    
    
    def decrypt_token(self,encrypted_token:EncryptedToken) -> Token:
        raw_value = encrypted_token.raw_value
        decoded : dict[str,str | datetime | UserRole] = jwt.decode(     #type: ignore
            raw_value,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        uid = decoded["sub"]
        if(not isinstance(uid,str)): raise ValueError("Impossible to parse ID")
        return Token(
            user_id=UserId(uid=int(uid)),
            role = UserRole(decoded["role"])
        )