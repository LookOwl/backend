from fastapi import FastAPI

from api.routes.books.bookController import router as r1
from api.routes.catalog.catalogController import router as r2
from api.routes.users.userController import router as r3

app = FastAPI()
app.include_router(prefix= "/api", router= r1 )
app.include_router(prefix= "/api", router= r2 )
app.include_router(prefix= "/api", router= r3 )


