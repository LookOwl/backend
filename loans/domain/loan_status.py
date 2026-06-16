from enum import Enum

class LoanStatus(Enum):
    PENDIENTE = "PENDIENTE"
    CANCELADO = "CANCELADO"
    ACTIVO = "ACTIVO"
    CONCLUIDO = "CONCLUIDO"
    PERDIDO = "PERDIDO"
    VENCIDO = "VENCIDO"
