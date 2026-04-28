from fastapi import APIRouter

router = APIRouter(prefix="/books",tags=["books"])

@router.get("/")
def getBooks():
    return "Imagine a list of books here"

@router.get("/search")
def searchBooks(title:str,author:str):
    return f"Tile {title}, author {author}"
