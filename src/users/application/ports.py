from abc import ABC, abstractmethod
from users.domain.token import Token
from users.domain.user import UserId, UserRole
from users.domain.user_credential import HashedPassword

class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self,password : str) -> HashedPassword:
        pass
    
    @abstractmethod
    def verify_password(self,hashed_password:HashedPassword, password : str) -> str:
        pass


class TokenHandler(ABC):

    @abstractmethod
    def generate_token(self,user_id : UserId, user_role : UserRole ) -> Token:
        pass
    
    @abstractmethod
    def decrypt_token(self,encrypted_token:str) -> Token:
        pass