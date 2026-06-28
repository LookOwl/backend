from dataclasses import dataclass

@dataclass
class HashedPassword:
    hashed : str

@dataclass
class UserCredentials:
    """ Represents the credential of a user """
    email : str
    stored_password: HashedPassword
