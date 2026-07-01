# DTOs Reference

DTOs are Pydantic v2 models that define the shape of request bodies. They live in `api/dtos/` and reuse a set of constrained types from `core/validators.py`.

A validation failure on any DTO field produces an HTTP `422 Unprocessable Entity` response with the standard FastAPI/Pydantic error structure.

---

## Shared validator types

These constrained `Annotated` types are used by multiple DTOs (`core/validators.py`).

| Type | Underlying | Constraints | Notes |
| --- | --- | --- | --- |
| `NonemptyString` | `str` | `min_length=1`, whitespace stripped | Rejects empty/whitespace-only strings. |
| `LanguageString` | `str` | exactly `2` characters, whitespace stripped | Intended as an ISO 639-1 language code (e.g. `"es"`, `"en"`). |
| `NonEmptyStringList` | `list[NonemptyString]` | `min_length=1` | At least one item; every item must be non-empty. |
| `PositiveInt` | `int` | `>= 1` | Strictly positive. |
| `NonNegativeInt` | `int` | `>= 0` | Zero allowed. |
| `PhoneNumberString` | `str` | exactly 9 digits, regex `^[0-9]{9}$` | Local phone-number format (no country code, no separators). |
| `IsbnString` | `str` | length 10–17 + ISBN-10/13 checksum validation | See **ISBN validation** below. |

### ISBN validation

`IsbnString` runs `core.validators.validate_isbn` after the length check.

The validator:

1. **Normalizes** the input by stripping spaces and dashes and upper-casing.
2. **Branches by length:**
   - **10 characters** — runs the ISBN-10 weighted checksum (weights 10..1). The check digit may be `X` (= 10).
   - **13 characters** — runs the ISBN-13 weighted checksum (alternating weights 1, 3).
   - **Any other length** — rejected.
3. Returns the **normalized** ISBN (no spaces, no dashes, uppercase) — this is what downstream code receives.
4. Raises `InvalidISBNException` (a `ValueError` subclass) on any failure; Pydantic surfaces this as `422`.

### `EmailStr`

Where you see `EmailStr` it is Pydantic's built-in email validator (RFC 5322-ish), provided by the `email-validator` package.

---

## DTOs

### `LoginDto`

Defined in `api/dtos/login_dto.py`. Used by `POST /api/users/login`.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `email` | `EmailStr` | yes | Must be a syntactically valid email. |
| `password` | `NonemptyString` | yes | Plain-text password sent over the wire; hashed server-side. |

Example:

```json
{
  "email": "lector@example.com",
  "password": "s3cret"
}
```

---

### `RegisterUserDto`

Defined in `api/dtos/login_dto.py`. Used by `POST /api/users/register`.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `fullname` | `NonemptyString` | yes | Full name of the user. |
| `contact_number` | `PhoneNumberString` | yes | Exactly 9 digits, no separators. |
| `email` | `EmailStr` | yes | Unique email; conflicts produce `409`. |
| `password` | `NonemptyString` | yes | Plain-text; hashed with `bcrypt` server-side before storage. |

The role of newly registered users is forced to `LECTOR` server-side (the client cannot set it).

Example:

```json
{
  "fullname": "Ana Pérez",
  "contact_number": "987654321",
  "email": "ana@example.com",
  "password": "s3cret"
}
```

---

### `RegisterBookDto`

Defined in `api/dtos/book_dto.py`. Used by `POST /api/books/register`.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `title` | `NonemptyString` | yes | Book title. |
| `isbn` | `IsbnString` | yes | ISBN-10 or ISBN-13. Stored normalized (no spaces/dashes, uppercase). |
| `description` | `NonemptyString` | yes | Free-form description. |
| `editorial` | `NonemptyString` | yes | Publisher name. |
| `publication_date` | `date` (ISO `YYYY-MM-DD`) | yes | Publication date. |
| `cover_url` | `AnyUrl` | yes | Must be a valid URL (any scheme accepted by Pydantic's `AnyUrl`). Stored as its string form. |
| `language` | `LanguageString` | yes | 2-letter language code. |
| `author` | `NonEmptyStringList` | yes | At least one author; each item non-empty. |
| `category` | `NonEmptyStringList` | yes | At least one category/genre. |
| `page_count` | `PositiveInt` | yes | Must be `>= 1`. |

Example:

```json
{
  "title": "El Aleph",
  "isbn": "978-84-9989-094-4",
  "description": "Colección de cuentos...",
  "editorial": "Debolsillo",
  "publication_date": "2011-05-19",
  "cover_url": "https://example.com/cover.jpg",
  "language": "es",
  "author": ["Jorge Luis Borges"],
  "category": ["Cuento", "Fantástico"],
  "page_count": 224
}
```

QA notes:

- ISBNs with valid format but bad checksum (e.g. `9788499890945`) must be rejected with `422`.
- ISBNs of length other than 10 or 13 (after normalization) must be rejected.
- `cover_url` must include a scheme (`http://`, `https://`, …); bare hostnames are rejected.
- `language` must be exactly 2 characters — `"esp"` or `"e"` are rejected.

---

### `SearchBookDto`

Defined in `api/dtos/book_dto.py`. **Not used directly as a request body** — the `GET /api/books/` controller constructs it from query parameters before passing it to the service. Documented here for completeness.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `title` | `NonemptyString \| None` | no | If provided, must be non-empty. |
| `author` | `NonemptyString \| None` | no | If provided, must be non-empty. |
| `limit` | `NonNegativeInt \| None` | no | Page size. Note: the controller adds `+1` to the value sent to the repository to compute `has_next`. |
| `offset` | `NonNegativeInt \| None` | no | Records to skip. |

---

## Domain models returned by the API

Responses currently serialize raw domain dataclasses. These are not DTOs but QA needs to know their shape.

### `Book` (`domain/book.py`)

| Field | Type |
| --- | --- |
| `id` | `int` |
| `title` | `str` |
| `isbn` | `str` |
| `description` | `str` |
| `editorial` | `str` |
| `publication_date` | `date` (serialized as ISO `YYYY-MM-DD`) |
| `cover_url` | `str` |
| `language` | `str` |
| `author` | `list[str]` |
| `category` | `list[str]` |
| `page_count` | `int` |

### Enums (not yet exposed via HTTP)

| Enum | Values | Used by |
| --- | --- | --- |
| `RolUsuario` (`domain/enums/roles_usuario.py`) | `bibliotecario`, `lector` | User role |
| `EstadoEjemplar` (`domain/enums/estado_ejemplares.py`) | `disponible`, `prestado`, `dañado` | Book copy status |
| `EstadoPrestamo` (`domain/enums/estado_prestamos.py`) | `pendiente`, `cancelado`, `activo`, `concluido`, `perdido`, `vencido` | Loan status |

---

## Validation error format

Any DTO validation failure produces the standard FastAPI response, e.g.:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

For ISBN failures the `type` is `value_error` and the `msg` includes the reason raised by `validate_isbn` (e.g. `"Invalid ISBN-13 Checksum"`).
