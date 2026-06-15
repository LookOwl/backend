from abc import ABC, abstractmethod
from users.domain.token import Token
from users.domain.user import UserId, UserRole

class PasswordHasher:
    @abstractmethod
    def hash_password(self,password : str) -> str:
        pass
    
    @abstractmethod
    def verify_password(self,hashed_password:str,password : str) -> str:
        pass


class TokenHandler:

    @abstractmethod
    def generate_token(user_id : UserId, user_role : UserRole ) -> Token:
        pass
    
    @abstractmethod
    def decrypt_token(encrypted_token:str) -> Token:
        pass