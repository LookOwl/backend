from fastapi import FastAPI

from api.controllers.books import router as r1
from api.controllers.users import router as r2

app = FastAPI()
app.include_router(prefix= "/api", router= r1 )
app.include_router(prefix= "/api", router= r2 )
