import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import Parentesco


class EstudianteAcudienteCreate(BaseModel):
    estudiante_id: uuid.UUID
    acudiente_id: uuid.UUID
    parentesco: Parentesco
    es_contacto_principal: bool = False


class EstudianteAcudienteRead(EstudianteAcudienteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
