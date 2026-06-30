from fastapi import Depends
from anthropic import AsyncAnthropic
from books.application.use_cases.get_book_recommendations import GetBookRecommendations
from books.application.use_cases.get_query_recommendations import GetQueryRecommendations
from books.application.use_cases.search_books import SearchBooks
from books.infrastructure.di import get_book_recommendations_uc, get_query_recommendations_uc, get_search_book_uc
from chatbot.application.ports import LLMPort, TokenCounterPort, ToolExecutorPort
from chatbot.application.use_cases.chat_orchestrator import ChatOrchestrator
from chatbot.domain.conversation_repository import ConversationRepository
from chatbot.infrastructure.adapters.anthropic_adapter import AnthropicAdapter
from chatbot.infrastructure.adapters.book_tool_executor import BookToolExecutor
from chatbot.infrastructure.adapters.sql_conversation_repository import SQLConversationRepository
from chatbot.infrastructure.adapters.token_counter import TokenizerCounterAdapter


def get_token_counter() -> TokenCounterPort:
    return TokenizerCounterAdapter()

def get_anthropic_llm() -> LLMPort:
    client = AsyncAnthropic()
    return AnthropicAdapter(client=client, model="deepseek-v4-flash")

def get_book_tool_executor(
    search_books_uc: SearchBooks = Depends(get_search_book_uc),
    book_recommendations_uc: GetBookRecommendations = Depends(get_book_recommendations_uc),
    query_recommendations_uc: GetQueryRecommendations = Depends(get_query_recommendations_uc)
) -> ToolExecutorPort:
    return BookToolExecutor(
        search_books_uc=search_books_uc,
        book_recommendations_uc=book_recommendations_uc,
        query_recommendations_uc=query_recommendations_uc,
    )

def get_conversation_repo() -> ConversationRepository:
    return SQLConversationRepository()

def get_chat_orchestrator(
    repo: ConversationRepository = Depends(get_conversation_repo),
    llm: LLMPort = Depends(get_anthropic_llm),
    token_counter: TokenCounterPort = Depends(get_token_counter),
    tool_executor: ToolExecutorPort = Depends(get_book_tool_executor),
) -> ChatOrchestrator:
    return ChatOrchestrator(
        repo=repo,
        llm=llm,
        token_counter=token_counter,
        tool_executor=tool_executor,
    )
