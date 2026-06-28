from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController
from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from loans.infrastructure.adapters.redis_loan_req_event_handler import RedisLoanRequestEventHandler
from shared.application.event_dispatcher_factory import EventDispatcherFactory
from shared.infrastructure.persistence.sql_drivers import engine
from shared.infrastructure.settings import settings
from books.infrastructure.http.http_controller import router as r1
from loans.infrastructure.http.http_controller import router as r2
from users.infrastructure.http.http_controller import router as r3
from books.infrastructure.http.http_controller import recommendations_router as r4

@asynccontextmanager
async def lifespan(app : FastAPI):
    app.state.redis : Redis =  Redis.from_url(  #type: ignore
        url=settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    #Before yielding, create all event dispatchers
    dispatcher = EventDispatcherFactory.create(
        dispatcher_cls=LoanRequestEventDispatcher,
        with_suscribers={
            RedisLoanRequestEventHandler : (
                RedisController(app.state.redis),
                RedisLockManager(app.state.redis)
            )
        }
    )
    app.state.loan_request_dispatcher = dispatcher
    yield
    await engine.dispose()
    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(prefix= "/api", router= r1 )
app.include_router(prefix= "/api", router= r2 )
app.include_router(prefix= "/api", router= r3 )
app.include_router(prefix= "/api", router= r4 )
