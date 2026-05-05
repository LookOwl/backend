from dataclasses import dataclass

@dataclass
class UserCredentials:
    uid : str
    email : str
    password : str
    role: str

@dataclass
class User:
    uid : str
    full_name : str
    contact_number : int
    role: str