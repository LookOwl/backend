from datetime import datetime, timedelta, timezone
import jwt
import bcrypt

SECRET_KEY = "This is a secret key. Do not share with anyone under any circumstances"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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