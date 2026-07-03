from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from loans.infrastructure.adapters.sql_loan_req_event_handler import SQLLoanRequestEventHandler
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController
from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from loans.infrastructure.adapters.redis_loan_req_event_handler import RedisLoanRequestEventHandler
from shared.application.event_dispatcher_factory import EventDispatcherFactory
from shared.infrastructure.persistence.sql_drivers import engine, async_session_factory
from shared.infrastructure.settings import settings
from books.infrastructure.http.controller.book_controller import router as r1
from books.infrastructure.http.controller.book_copy_controller import router as r2
from books.infrastructure.http.controller.recommendation_controller import router as r3
from loans.infrastructure.http.request_http_controller import router as r4
from loans.infrastructure.http.loan_http_controller import router as r7
from users.infrastructure.http.http_controller import router as r5
from chatbot.infrastructure.http.controller.chat_controller import router as r6

from apscheduler.schedulers.asyncio import AsyncIOScheduler #type: ignore
from loans.infrastructure.workers.loan_request_checker import LoanRequestConsistencySubject

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app : FastAPI):
    app.state.redis : Redis =  Redis.from_url(  #type: ignore
        url=settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    #Before yielding, create all event dispatchers
    dispatcher = await EventDispatcherFactory.create(
        dispatcher_cls=LoanRequestEventDispatcher,
        with_suscribers={
            RedisLoanRequestEventHandler : (
                RedisController(app.state.redis),
                RedisLockManager(app.state.redis)
            ),
            SQLLoanRequestEventHandler : (
                async_session_factory,
            )
        }
    )
    assert isinstance(dispatcher,LoanRequestEventDispatcher)

    app.state.loan_request_dispatcher = dispatcher

    async def worker():
        async with async_session_factory() as session:
            dispatcher = app.state.loan_request_dispatcher
            checker = LoanRequestConsistencySubject(session,dispatcher)
            await checker.execute()
    
    scheduler.add_job(worker,"interval",minutes=1)  #type: ignore
    scheduler.start()
    
    yield
    scheduler.shutdown()
    await engine.dispose()
    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(prefix= "/api", router= r1 )
app.include_router(prefix= "/api", router= r2 )
app.include_router(prefix= "/api", router= r3 )
app.include_router(prefix= "/api", router= r4 )
app.include_router(prefix= "/api", router= r5 )
app.include_router(prefix= "/api", router= r6 )
app.include_router(prefix="/api",router = r7)
