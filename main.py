from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from old.infrastructure.database.connection import engine
from old.infrastructure.redis.redis_seed import seed
from old.infrastructure.config.config import settings
from old.api.controllers.books import router as r1
from old.api.controllers.users import router as r2

@asynccontextmanager
async def lifespan(app : FastAPI):
    app.state.redis : Redis =  Redis.from_url(  #type: ignore
        url=settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    await seed(app.state.redis)
    yield
    await engine.dispose()
    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(prefix= "/api", router= r1 )
app.include_router(prefix= "/api", router= r2 )