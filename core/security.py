from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from fastapi import Security, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from repositories.user_repository import UserRepository
from repositories.exports.di import get_user_repository

SECRET_KEY = "This is a secret key. Do not share with anyone under any circumstances"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

BEARER = HTTPBearer()

def hash_password(
    password : str
) -> str:
    return bcrypt.hashpw(
        password = password.encode("utf-8"),
        salt = bcrypt.gensalt()
    ).decode("utf-8")



def verify_password(password : str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password= password.encode("utf-8"),
        hashed_password=hashed_password.encode("utf-8")
    )

def generate_token(
    user_id : str,
    user_role : str
):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub" : user_id,
        "exp" : expire,
        "iat" : now,
        "iss" : "LookOwl-Server" ,
        "role" : user_role
    }
    return jwt.encode(
        payload = payload,
        key = SECRET_KEY,
        algorithm = ALGORITHM
    )


def decode_token(token : str):
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms = [ ALGORITHM ]
    )

async def extract_user(
    credentials: HTTPAuthorizationCredentials = Security(BEARER),
    user_repo : UserRepository = Depends(get_user_repository)
):
    try:
        print("inside guard")
        payload = decode_token(credentials.credentials)
        print(payload)
        user  = user_repo.get_user_by_id(int(payload['sub']))
        print(user)
        if user is None:
            raise ValueError
        return user

    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
                status_code=409,
                detail="Invalid token or user"
            )
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Fatal error. ID could be not an int"
        )
