from typing import Annotated
from annotated_types import Len, Ge
from pydantic import StringConstraints, AfterValidator, AnyUrl
from core.exceptions import InvalidISBNException

NonemptyString = Annotated[
    str,
    StringConstraints(
        min_length=1,
        strip_whitespace=True
    )
]

LanguageString = Annotated[
    str,
    StringConstraints(
        min_length=2,
        max_length=2,
        strip_whitespace=True
    )
]

NonEmptyStringList = Annotated[
    list[NonemptyString],
    Len(
        min_len = 1
    )
]

PositiveInt = Annotated[
    int,
    Ge(1)
]

PhoneNumberString = Annotated[
    str,
    StringConstraints(
        min_length=9,
        max_length=9,
        pattern=r"^[0-9]{9}$"
    )
]

def validate_isbn(isbn : str):
    normalized = (
        isbn.replace(" ","")
            .replace("-","")
            .upper()
    )
    try:
        match len(normalized):
            case 10:
                sum = 0
                for i in range(9):
                    sum += i * int(normalized[i])
                checksum = sum % 11
                if checksum == 10 and normalized[-1] != 'X':
                    raise InvalidISBNException("Invalid ISBN-10 Checksum")
                elif int(normalized[-1]) != checksum:
                    raise InvalidISBNException("Invalid ISBN-10 Checksum")
            case 13:
                sum = 0
                for i in range(9):
                    weight = 1 if i % 2 == 0 else 3
                    sum += weight * int(normalized[i])
                checksum = sum % 10
                if checksum != 0:
                    raise InvalidISBNException("Invalid ISBN-13 Checksum")
            case _ :
                raise InvalidISBNException("Only ISBN-10 and ISBN-13 formats are allowed")
    except InvalidISBNException as e:
        raise e
    except Exception as e:
        raise InvalidISBNException("Error parsing ISBN") 
    
    return isbn

IsbnString = Annotated[
    str,
    StringConstraints(
        min_length=10,
        max_length=13
    ),
    AfterValidator(validate_isbn)
]

