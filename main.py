from fastapi import FastAPI
from contextlib import asynccontextmanager
from infrastructure.database.connection import engine
from api.controllers.books import router as r1
from api.controllers.users import router as r2

@asynccontextmanager
async def lifespan(app : FastAPI):
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(prefix= "/api", router= r1 )
app.include_router(prefix= "/api", router= r2 )
