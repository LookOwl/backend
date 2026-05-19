from enum import Enum

class EstadoPrestamo(Enum):
    PENDIENTE = "pendiente"
    CANCELADO = "cancelado"
    ACTIVO = "activo"
    CONCLUIDO = "concluido"
    PERDIDO = "perdido"
    VENCIDO = "vencido"
