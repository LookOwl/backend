import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from db.base import Base
from repositories.book_repository import BookRepository
from domain.book import Book


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def crear_libro(**overrides) -> Book:
    return Book(
        uid=overrides.get("uid", "1"),
        title=overrides.get("title", "Libro de Prueba"),
        isbn=overrides.get("isbn", "1111111111111"),
        description=overrides.get("description", "Descripción de prueba"),
        editorial=overrides.get("editorial", "Editorial de Prueba"),
        publication_date=overrides.get("publication_date", date.today()),
        cover_url=overrides.get("cover_url", "http://example.com/cover.jpg"),
        language=overrides.get("language", "es"),
        author=overrides.get("author", ["John Smith"]),
        category=overrides.get("category", ["Python"]),
        page_count=overrides.get("page_count", 123),
        n_copies=overrides.get("n_copies", 1),
    )


def test_guardar_libro_valido(db_session):
    repo = BookRepository(db_session)
    book = crear_libro(uid="1", isbn="1111111111111")

    saved = repo.save_book(book)

    assert saved.title == book.title
    assert saved.isbn == book.isbn
    assert "John Smith" in saved.author
    assert "Python" in saved.category


def test_guardar_libro_isbn_duplicado_error(db_session):
    repo = BookRepository(db_session)
    book1 = crear_libro(uid="1", isbn="2222222222222")
    book2 = crear_libro(uid="2", isbn="2222222222222")

    repo.save_book(book1)

    with pytest.raises(IntegrityError):
        repo.save_book(book2)


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": ""},
        {"title": "A" * 256},
        {"isbn": "4" * 14},
        {"editorial": "E" * 101},
        {"cover_url": "h" * 501},
        {"language": "spa"},
    ],
)
def test_guardar_libro_datos_invalidos_error(db_session, overrides):
    repo = BookRepository(db_session)
    datos = {"uid": "1", "isbn": "3333333333333"}
    datos.update(overrides)
    book = crear_libro(**datos)

    with pytest.raises(ValueError):
        repo.save_book(book)
