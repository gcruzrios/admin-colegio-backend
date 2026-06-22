from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cargo import Cargo
from app.models.enums import EstadoCargo


def actualizar_estado_cargo(db: Session, cargo: Cargo) -> None:
    """Recalcula el estado de un cargo según la suma de sus pagos."""
    total_pagado = sum((pago.monto for pago in cargo.pagos), Decimal("0"))
    if total_pagado <= 0:
        cargo.estado = EstadoCargo.PENDIENTE
    elif total_pagado < cargo.monto:
        cargo.estado = EstadoCargo.PARCIAL
    else:
        cargo.estado = EstadoCargo.PAGADO
    db.commit()
