

from pydantic import BaseModel


class ReturnBookDto(BaseModel):
    book_physical_copy_code : str