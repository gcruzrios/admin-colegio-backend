import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, requiere_roles
from app.models.enums import RolUsuario
from app.models.grupo import Grupo
from app.models.usuario import Usuario
from app.schemas.grupo import GrupoCreate, GrupoRead, GrupoUpdate

router = APIRouter(prefix="/grupos", tags=["Grupos"])


@router.get("/", response_model=list[GrupoRead])
def listar_grupos(anio_escolar_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(Grupo).filter(Grupo.activo == True)  # noqa: E712
    if anio_escolar_id:
        query = query.filter(Grupo.anio_escolar_id == anio_escolar_id)
    return query.order_by(Grupo.nombre).all()


@router.get("/mi-grupo", response_model=list[GrupoRead], dependencies=[Depends(requiere_roles(RolUsuario.PROFESOR))])
def mi_grupo(db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    return db.query(Grupo).filter(Grupo.profesor_guia_id == usuario_actual.id, Grupo.activo == True).all()  # noqa: E712


@router.post(
    "/", response_model=GrupoRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)
def crear_grupo(datos: GrupoCreate, db: Session = Depends(get_db)):
    grupo = Grupo(**datos.model_dump())
    db.add(grupo)
    db.commit()
    db.refresh(grupo)
    return grupo


@router.put("/{grupo_id}", response_model=GrupoRead, dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))])
def actualizar_grupo(grupo_id: uuid.UUID, datos: GrupoUpdate, db: Session = Depends(get_db)):
    grupo = db.get(Grupo, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(grupo, campo, valor)
    db.commit()
    db.refresh(grupo)
    return grupo
