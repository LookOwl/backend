from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from infrastructure.database.connection import engine
from infrastructure.redis.redis_seed import seed
from infrastructure.config.config import settings
from api.controllers.books import router as r1
from api.controllers.users import router as r2

@asynccontextmanager
async def lifespan(app : FastAPI):
    app.state.redis =  Redis.from_url(
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
