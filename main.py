from fastapi import FastAPI

from api.controllers.books import router as r1
from api.controllers.catalog import router as r2
from api.controllers.auth import router as r3

app = FastAPI()
app.include_router(prefix= "/api", router= r1 )
app.include_router(prefix= "/api", router= r2 )
app.include_router(prefix= "/api", router= r3 )


