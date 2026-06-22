import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import MetodoPago


class PagoCreate(BaseModel):
    cargo_id: uuid.UUID
    monto: Decimal
    fecha_pago: date
    metodo_pago: MetodoPago
    observaciones: str | None = None


class PagoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    cargo_id: uuid.UUID
    monto: Decimal
    fecha_pago: date
    metodo_pago: MetodoPago
    numero_recibo: str
    observaciones: str | None
