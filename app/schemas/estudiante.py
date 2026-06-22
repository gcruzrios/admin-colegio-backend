import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import Genero


class EstudianteBase(BaseModel):
    nombre_completo: str
    identificacion: str | None = None
    fecha_nacimiento: date
    genero: Genero | None = None


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(BaseModel):
    nombre_completo: str | None = None
    identificacion: str | None = None
    fecha_nacimiento: date | None = None
    genero: Genero | None = None
    activo: bool | None = None


class EstudianteRead(EstudianteBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    activo: bool
