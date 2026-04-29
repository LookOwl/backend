from pydantic import BaseModel

class RegisterBookDto(BaseModel):
    portrait : str
    title : str
    author : str
    category : str
    isbn : str
