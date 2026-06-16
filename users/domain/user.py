from dataclasses import dataclass
from users.domain.user_role import UserRole
from users.domain.user_credential import UserCredentials
from users.domain.user_id import UserId

@dataclass
class User:
    id: UserId
    full_name: str
    contact_number: str
    role: UserRole
    credentials: UserCredentials