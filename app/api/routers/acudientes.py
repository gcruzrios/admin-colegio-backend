from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import requiere_roles
from app.models.enums import RolUsuario
from app.models.estudiante_acudiente import EstudianteAcudiente
from app.schemas.estudiante_acudiente import EstudianteAcudienteCreate, EstudianteAcudienteRead

router = APIRouter(
    prefix="/acudientes", tags=["Acudientes"], dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)


@router.post("/vincular", response_model=EstudianteAcudienteRead, status_code=status.HTTP_201_CREATED)
def vincular_acudiente(datos: EstudianteAcudienteCreate, db: Session = Depends(get_db)):
    vinculo = EstudianteAcudiente(**datos.model_dump())
    db.add(vinculo)
    db.commit()
    db.refresh(vinculo)
    return vinculo
