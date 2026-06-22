import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import RolUsuario


class UsuarioBase(BaseModel):
    nombre_completo: str
    email: EmailStr
    rol: RolUsuario
    telefono: str | None = None
    identificacion: str | None = None
    asignatura: str | None = None


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    nombre_completo: str | None = None
    telefono: str | None = None
    identificacion: str | None = None
    asignatura: str | None = None
    activo: bool | None = None


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    activo: bool
    created_at: datetime
