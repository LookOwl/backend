from unittest.mock import AsyncMock
import pytest
from books.application.use_cases.search_books import SearchBooks
from books.domain.book import (
    Book,
    BookAuthor,
    BookCategory,
    BookDescription,
    BookId,
    BookLanguage,
    BookTitle,
)
from books.domain.book_search_criteria import BookSearchCriteria
from books.domain.result_page import ResultPage


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


class TestSearchBooks:

    @pytest.mark.asyncio
    async def test_search_by_query_returns_matching_books(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        expected = [_make_book(1, "Cien Años de Soledad", ["García Márquez"])]
        mock_book_repo.search_book.return_value = expected
        uc = SearchBooks(mock_book_repo, fake_uow)

        # Act
        result = await uc.execute(
            query="Cien Años de Soledad", limit=10, offset=0
        )

        # Assert
        assert result == expected
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_returns_empty_list_when_no_match(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_book_repo.search_book.return_value = []
        uc = SearchBooks(mock_book_repo, fake_uow)

        # Act
        result = await uc.execute(query="Nonexistent", limit=10, offset=0)

        # Assert
        assert result == []
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_passes_pagination_params(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_book_repo.search_book.return_value = []
        uc = SearchBooks(mock_book_repo, fake_uow)

        # Act
        await uc.execute(query="Orwell", limit=5, offset=20)

        # Assert: verify the pagination values were forwarded
        call_args = mock_book_repo.search_book.call_args
        page: ResultPage = call_args[0][1]  # second positional arg
        assert page.starts_at == 20
        assert page.number_of_results == 5
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_passes_correct_query_to_repo(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_book_repo.search_book.return_value = []
        uc = SearchBooks(mock_book_repo, fake_uow)

        # Act
        await uc.execute(query="1984", limit=10, offset=0)

        # Assert
        call_args = mock_book_repo.search_book.call_args
        criteria: BookSearchCriteria = call_args[0][0]
        assert criteria.query.query == "1984"
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_search_rolls_back_on_repository_error(
        self, mock_book_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_book_repo.search_book.side_effect = RuntimeError("DB down")
        uc = SearchBooks(mock_book_repo, fake_uow)

        # Act & Assert
        with pytest.raises(RuntimeError, match="DB down"):
            await uc.execute(query="test", limit=10, offset=0)

        assert not fake_uow.committed  # UOW should roll back, not commit
