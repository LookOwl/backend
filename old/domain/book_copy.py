from dataclasses import dataclass
from old.domain.enums.estado_ejemplares import EstadoEjemplar

@dataclass
class BookCopy:
    libro_id : int
    codigo: str
    estado: EstadoEjemplar

