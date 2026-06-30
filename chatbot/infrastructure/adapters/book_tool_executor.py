from books.application.use_cases.get_book_recommendations import GetBookRecommendations
from books.application.use_cases.get_query_recommendations import GetQueryRecommendations
from books.application.use_cases.search_books import SearchBook
from books.domain.book import Book, BookId
from chatbot.application.ports import ToolExecutorPort
from chatbot.domain.message import ToolCall


class BookToolExecutor(ToolExecutorPort):

    def __init__(
        self,
        search_books_uc: SearchBook,
        book_recommendations_uc: GetBookRecommendations,
        query_recommendations_uc: GetQueryRecommendations,
    ) -> None:
        self._search_books = search_books_uc
        self._book_recommendations = book_recommendations_uc
        self._query_recommendations = query_recommendations_uc

    async def execute(self, tool_call: ToolCall) -> str:
        match tool_call.name:
            case "search_books":
                return await self._handle_search_books(tool_call.arguments)
            case "recommend_books_by_query":
                return await self._handle_recommend_by_query(tool_call.arguments)
            case "recommend_books_by_id":
                return await self._handle_recommend_by_id(tool_call.arguments)
            case _:
                return f"Error: herramienta desconocida '{tool_call.name}'"

    async def _handle_search_books(self, args: dict) -> str:
        query = args.get("query", "")
        # TODO: Replace with actual semantic search by pattern
        try:
            results = await self._query_recommendations.execute(
                query=query, num_recommendations=10
            )
        except Exception:
            results = await self._search_books.execute(
                title=query,
                authors=[],
                limit=10,
                offset=0,
            )
        return self._format_books(results)

    async def _handle_recommend_by_query(self, args: dict) -> str:
        query = args.get("query", "")
        results = await self._query_recommendations.execute(
            query=query, num_recommendations=5
        )
        return self._format_books(results)

    async def _handle_recommend_by_id(self, args: dict) -> str:
        book_id = args.get("book_id")
        if book_id is None:
            return "Error: 'book_id' es requerido"
        results = await self._book_recommendations.execute(
            book_id=BookId(id=int(book_id)), num_recommendations=5
        )
        return self._format_books(results)

    def _format_books(self, books: list[Book]) -> str:
        if not books:
            return "No se encontraron libros."

        lines = ["Resultados de búsqueda:"]
        for i, book in enumerate(books, 1):
            title = book.title.title
            authors = ", ".join(book.author.authors)
            lang = book.language.lang
            cats = ", ".join(book.category.categories)
            desc = (
                (book.description.description[:120] + "...")
                if len(book.description.description) > 120
                else book.description.description
            )
            lines.append(
                f"{i}. {title} — {authors} ({lang})"
                f"\n   Categorías: {cats}"
                f"\n   {desc}"
            )
        return "\n\n".join(lines)
