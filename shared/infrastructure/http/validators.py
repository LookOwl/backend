from typing import Annotated
from annotated_types import Len, Ge
from fastapi import HTTPException
from pydantic import StringConstraints, AfterValidator

NonEmptyString = Annotated[
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
    list[NonEmptyString],
    Len(
        min_length= 1
    )
]

PositiveInt = Annotated[
    int,
    Ge(1)
]

NonNegativeInt = Annotated[
    int,
    Ge(0)
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
                total = 0
                normalized = normalized.upper()
                for i in range(9):
                    weight = 10 - i
                    try:
                        digit = int(normalized[i])
                    except Exception:
                        raise Exception("Invalid character in ISBN-10")
                    total += weight * digit

                check_char = normalized[9]
                if check_char == 'X':
                    check_value = 10
                else:
                    try:
                        check_value = int(check_char)
                    except Exception:
                        raise Exception("Invalid character in ISBN-10 check digit")

                total += check_value
                if total % 11 != 0:
                    raise Exception("Invalid ISBN-10 Checksum")
            case 13:
                total = 0
                try:
                    for i in range(13):
                        weight = 1 if i % 2 == 0 else 3
                        total += weight * int(normalized[i])
                except Exception:
                    raise Exception("Invalid character in ISBN-13")
                checksum = total % 10
                if checksum != 0:
                    raise Exception("Invalid ISBN-13 Checksum")
            case _ :
                raise Exception("Only ISBN-10 and ISBN-13 formats are allowed")
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail="Error parsing ISBN"
            ) from e 
    
    return normalized

IsbnString = Annotated[
    str,
    StringConstraints(
        min_length=10,
        max_length=17
    ),
    AfterValidator(validate_isbn)
]


