from dataclasses import dataclass

@dataclass
class Book:
    uid : str
    title : str
    author : str
    category : str
    isbn : str
    n_copies : int

