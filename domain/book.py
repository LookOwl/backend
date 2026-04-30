from dataclasses import dataclass
from datetime import date

@dataclass
class Book:
    uid : int
    title : str
    isbn : str
    description : str
    editorial : str
    publication_date : date
    cover_url : str
    language : str
    author : list[str]
    category : list[str]
    page_count : int
    n_copies : int
