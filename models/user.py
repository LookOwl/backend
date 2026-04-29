from dataclasses import dataclass

@dataclass
class UserCredentials:
    uid : str
    email : str
    password : str
@dataclass
class User:
    uid : str
    full_name : str
    fullname : str
    contact_number : int
    email : str
    password : str