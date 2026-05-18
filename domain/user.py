from dataclasses import dataclass
from domain.enums.roles_usuario import RolUsuario

@dataclass
class UserCredentials:
    password_hash: str

@dataclass
class User:
    uid: str
    full_name: str
    email: str
    contact_number: str
    role: RolUsuario
    credentials: UserCredentials
