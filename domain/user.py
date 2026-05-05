from dataclasses import dataclass

@dataclass
class UserCredentials:
    password_hash: str

@dataclass
class User:
    uid: str
    full_name: str
    email: str
    contact_number: str
    role: str
    credentials: UserCredentials
