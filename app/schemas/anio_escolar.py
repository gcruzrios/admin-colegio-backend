import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class AnioEscolarCreate(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    activo: bool = False


class AnioEscolarRead(AnioEscolarCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
