from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import requiere_roles
from app.models.anio_escolar import AnioEscolar
from app.models.enums import RolUsuario
from app.schemas.anio_escolar import AnioEscolarCreate, AnioEscolarRead

router = APIRouter(prefix="/anios-escolares", tags=["Años escolares"])


@router.get("/", response_model=list[AnioEscolarRead])
def listar_anios(db: Session = Depends(get_db)):
    return db.query(AnioEscolar).order_by(AnioEscolar.nombre.desc()).all()


@router.post(
    "/",
    response_model=AnioEscolarRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))],
)
def crear_anio_escolar(datos: AnioEscolarCreate, db: Session = Depends(get_db)):
    if datos.activo:
        db.query(AnioEscolar).update({AnioEscolar.activo: False})
    anio = AnioEscolar(**datos.model_dump())
    db.add(anio)
    db.commit()
    db.refresh(anio)
    return anio
