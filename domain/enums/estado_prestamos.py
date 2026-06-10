from enum import Enum

class EstadoPrestamo(Enum):
    PENDIENTE = "PENDIENTE"
    CANCELADO = "CANCELADO"
    ACTIVO = "ACTIVO"
    CONCLUIDO = "CONCLUIDO"
    PERDIDO = "PERDIDO"
    VENCIDO = "VENCIDO"
