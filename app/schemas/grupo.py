import uuid

from pydantic import BaseModel, ConfigDict


class GrupoBase(BaseModel):
    nombre: str
    nivel: str
    anio_escolar_id: uuid.UUID
    profesor_guia_id: uuid.UUID | None = None
    capacidad_maxima: int | None = None


class GrupoCreate(GrupoBase):
    pass


class GrupoUpdate(BaseModel):
    nombre: str | None = None
    nivel: str | None = None
    profesor_guia_id: uuid.UUID | None = None
    capacidad_maxima: int | None = None
    activo: bool | None = None


class GrupoRead(GrupoBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    activo: bool
