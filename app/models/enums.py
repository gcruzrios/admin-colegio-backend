import enum


class RolUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    PROFESOR = "PROFESOR"
    PADRE = "PADRE"


class TipoCargo(str, enum.Enum):
    MATRICULA = "MATRICULA"
    MENSUALIDAD = "MENSUALIDAD"
    MATERIAL = "MATERIAL"
    OTRO = "OTRO"


class EstadoCargo(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PARCIAL = "PARCIAL"
    PAGADO = "PAGADO"
    VENCIDO = "VENCIDO"
    ANULADO = "ANULADO"


class EstadoMatricula(str, enum.Enum):
    ACTIVA = "ACTIVA"
    RETIRADO = "RETIRADO"
    GRADUADO = "GRADUADO"
    TRASLADADO = "TRASLADADO"


class MetodoPago(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    SINPE_MOVIL = "SINPE_MOVIL"
    TARJETA = "TARJETA"
    CHEQUE = "CHEQUE"


class Parentesco(str, enum.Enum):
    MADRE = "MADRE"
    PADRE = "PADRE"
    TUTOR = "TUTOR"
    OTRO = "OTRO"


class Genero(str, enum.Enum):
    M = "M"
    F = "F"
    OTRO = "OTRO"
