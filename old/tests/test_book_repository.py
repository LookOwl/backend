import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from old.infrastructure.database.base import Base
from old.repositories.book_repository import BookRepository
from old.domain.book import Book


@pytest.fixture
async def db_session():
    import old.infrastructure.database.models.usuario  
    import old.infrastructure.database.models.libro  
    import old.infrastructure.database.models.ejemplar  
    import old.infrastructure.database.models.prestamo  
    import old.infrastructure.database.models.solicitud_libro  
    import old.infrastructure.database.models.autor  
    import old.infrastructure.database.models.genero  
    import old.infrastructure.database.models.libro_embedding  

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session


def crear_libro(**overrides) -> Book:
    return Book(
        id=overrides.get("uid", 0),
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
    )


@pytest.mark.asyncio
async def test_guardar_libro_valido(db_session: AsyncSession):
    repo = BookRepository(db_session)
    book = crear_libro(uid=1, isbn="1111111111111")

    saved = await repo.save_book(book)

    assert saved.title == book.title
    assert saved.isbn == book.isbn
    assert "John Smith" in saved.author
    assert "Python" in saved.category


@pytest.mark.asyncio
async def test_guardar_libro_isbn_duplicado_error(db_session: AsyncSession):
    repo = BookRepository(db_session)
    book1 = crear_libro(uid=1, isbn="2222222222222")
    book2 = crear_libro(uid=2, isbn="2222222222222")

    await repo.save_book(book1)

    with pytest.raises(IntegrityError):
        await repo.save_book(book2)


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
@pytest.mark.asyncio
async def test_guardar_libro_datos_invalidos_error(db_session: AsyncSession, overrides):
    repo = BookRepository(db_session)
    datos = {"uid": 1, "isbn": "3333333333333"}
    datos.update(overrides)
    book = crear_libro(**datos)

    with pytest.raises(ValueError):
        await repo.save_book(book)
