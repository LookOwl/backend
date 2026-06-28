from pydantic import BaseModel, NonNegativeInt
from shared.infrastructure.http.validators import NonEmptyString


class SearchBookDto(BaseModel):
    title : NonEmptyString | None
    author : NonEmptyString | None
    limit : NonNegativeInt | None
    offset : NonNegativeInt | None