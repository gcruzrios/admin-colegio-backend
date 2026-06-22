import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import EstadoMatricula


class MatriculaCreate(BaseModel):
    estudiante_id: uuid.UUID
    grupo_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    fecha_matricula: date


class MatriculaUpdate(BaseModel):
    estado: EstadoMatricula | None = None
    grupo_id: uuid.UUID | None = None


class MatriculaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    estudiante_id: uuid.UUID
    grupo_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    fecha_matricula: date
    estado: EstadoMatricula
