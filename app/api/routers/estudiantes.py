import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, requiere_roles
from app.models.enums import RolUsuario
from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.schemas.estudiante import EstudianteCreate, EstudianteRead, EstudianteUpdate

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


@router.get(
    "/",
    response_model=list[EstudianteRead],
    dependencies=[Depends(requiere_roles(RolUsuario.ADMIN, RolUsuario.PROFESOR))],
)
def listar_estudiantes(db: Session = Depends(get_db)):
    return db.query(Estudiante).filter(Estudiante.activo == True).order_by(Estudiante.nombre_completo).all()  # noqa: E712


@router.get(
    "/mis-hijos", response_model=list[EstudianteRead], dependencies=[Depends(requiere_roles(RolUsuario.PADRE))]
)
def mis_hijos(db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    ids = [v.estudiante_id for v in usuario_actual.vinculos_estudiantes]
    return db.query(Estudiante).filter(Estudiante.id.in_(ids)).all()


@router.post(
    "/",
    response_model=EstudianteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))],
)
def crear_estudiante(datos: EstudianteCreate, db: Session = Depends(get_db)):
    estudiante = Estudiante(**datos.model_dump())
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante


@router.get("/{estudiante_id}", response_model=EstudianteRead)
def obtener_estudiante(
    estudiante_id: uuid.UUID, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)
):
    estudiante = db.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    if usuario_actual.rol == RolUsuario.PADRE:
        vinculo = any(v.estudiante_id == estudiante_id for v in usuario_actual.vinculos_estudiantes)
        if not vinculo:
            raise HTTPException(status_code=403, detail="No tienes acceso a este estudiante")
    return estudiante


@router.put("/{estudiante_id}", response_model=EstudianteRead, dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))])
def actualizar_estudiante(estudiante_id: uuid.UUID, datos: EstudianteUpdate, db: Session = Depends(get_db)):
    estudiante = db.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(estudiante, campo, valor)
    db.commit()
    db.refresh(estudiante)
    return estudiante


@router.delete(
    "/{estudiante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))],
)
def desactivar_estudiante(estudiante_id: uuid.UUID, db: Session = Depends(get_db)):
    estudiante = db.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    estudiante.activo = False
    db.commit()
