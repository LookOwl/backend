from users.application.ports import PasswordHasher
import bcrypt

from users.domain.user_credential import HashedPassword 

class BcryptPasswordHasher(PasswordHasher):
    
    def __init__(self) -> None:
        super().__init__()
        return

    def hash_password(self,password : str) -> HashedPassword:
        return HashedPassword(
            bcrypt.hashpw(
                password=password.encode("utf-8"),
                salt=bcrypt.gensalt()
            ).decode("utf-8")
        )
    
    
    def verify_password(self,hashed_password:HashedPassword, password : str) -> bool:
        return bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=hashed_password.hashed.encode("utf-8")
        )