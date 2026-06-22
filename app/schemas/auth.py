from pydantic import BaseModel

from app.models.enums import RolUsuario


class Token(BaseModel):
    access_token: str
    token_type: str
    rol: RolUsuario
    nombre_completo: str
