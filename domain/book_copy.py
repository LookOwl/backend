from dataclasses import dataclass
from domain.enums.estado_ejemplares import EstadoEjemplar

@dataclass
class BookCopy:
    codigo: str
    estado: EstadoEjemplar
