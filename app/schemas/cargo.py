import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import EstadoCargo, TipoCargo


class CargoCreate(BaseModel):
    estudiante_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    tipo: TipoCargo
    descripcion: str
    monto: Decimal
    mes_correspondiente: int | None = None
    fecha_emision: date
    fecha_vencimiento: date


class CargoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    estudiante_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    tipo: TipoCargo
    descripcion: str
    monto: Decimal
    mes_correspondiente: int | None
    fecha_emision: date
    fecha_vencimiento: date
    estado: EstadoCargo


class GenerarMensualidadesRequest(BaseModel):
    anio_escolar_id: uuid.UUID
    mes: int
    monto: Decimal
    fecha_vencimiento: date
