from datetime import date
from unittest.mock import AsyncMock

import pytest

from books.application.use_cases.search_books import SearchBook
from books.domain.book import (
    Book,
    BookAuthor,
    BookCategory,
    BookDescription,
    BookId,
    BookLanguage,
    BookTitle,
)


def _make_book(book_id: int, title: str, authors: list[str]) -> Book:
    """Helper to create a minimal Book for assertions."""
    return Book(
        book_id=BookId(book_id),
        title=BookTitle(title),
        isbn=None,
        description=BookDescription("desc"),
        editorial=None,
        publication_date=None,
        cover_url=None,
        language=BookLanguage("es"),
        author=BookAuthor(authors),
        category=BookCategory(["Ficción"]),
        page_count=None,
    )


class TestSearchBook:

    @pytest.mark.asyncio
    async def test_search_by_title_returns_matching_books(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        expected = [_make_book(1, "Cien Años de Soledad", ["García Márquez"])]
        mock_book_repo.find_by_criteria.return_value = expected
        uc = SearchBook(mock_book_repo, fake_uow)

        # Act
        result = await uc.execute(
            title="Cien Años de Soledad", authors=[], limit=10, offset=0
        )

        # Assert
        assert result == expected
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_by_author_returns_matching_books(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        expected = [
            _make_book(1, "Cien Años de Soledad", ["García Márquez"]),
            _make_book(2, "El amor en los tiempos del cólera", ["García Márquez"]),
        ]
        mock_book_repo.find_by_criteria.return_value = expected
        uc = SearchBook(mock_book_repo, fake_uow)

        # Act
        result = await uc.execute(
            title=None, authors=["García Márquez"], limit=10, offset=0
        )

        # Assert
        assert len(result) == 2
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_returns_empty_list_when_no_match(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_book_repo.find_by_criteria.return_value = []
        uc = SearchBook(mock_book_repo, fake_uow)

        # Act
        result = await uc.execute(
            title="Nonexistent", authors=[], limit=10, offset=0
        )

        # Assert
        assert result == []
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_passes_pagination_params(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_book_repo.find_by_criteria.return_value = []
        uc = SearchBook(mock_book_repo, fake_uow)

        # Act
        await uc.execute(title=None, authors=["Orwell"], limit=5, offset=20)

        # Assert: verify the pagination values were forwarded
        call_args = mock_book_repo.find_by_criteria.call_args
        _, kwargs = call_args  # (criteria, page)
        page_arg = call_args[0][1]  # second positional arg is ResultPage
        assert page_arg.starts_at == 20
        assert page_arg.number_of_results == 5
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_with_both_title_and_author(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        expected = [_make_book(1, "1984", ["George Orwell"])]
        mock_book_repo.find_by_criteria.return_value = expected
        uc = SearchBook(mock_book_repo, fake_uow)

        # Act
        result = await uc.execute(
            title="1984", authors=["George Orwell"], limit=10, offset=0
        )

        # Assert
        assert result == expected
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_rolls_back_on_repository_error(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_book_repo.find_by_criteria.side_effect = RuntimeError("DB down")
        uc = SearchBook(mock_book_repo, fake_uow)

        # Act & Assert
        with pytest.raises(RuntimeError, match="DB down"):
            await uc.execute(title=None, authors=[], limit=10, offset=0)

        assert not fake_uow.committed  # UOW should roll back, not commit
