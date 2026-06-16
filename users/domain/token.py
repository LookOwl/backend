from dataclasses import dataclass
from users.domain.user_id import UserId
from users.domain.user_role import UserRole

@dataclass
class Token:
    user_id : UserId
    role : UserRole

@dataclass
class EncryptedToken:
    raw_value : str