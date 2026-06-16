

class InvalidISBNException(ValueError):
    def __init__(self,*args):
        super().__init__(*args)

    def __str__(self):
        return super().__str__()
    
class BookNotCreatedException(Exception):
    def __init__(self,*args):
        super().__init__(*args)

    def __str__(self):
        return super().__str__()
    