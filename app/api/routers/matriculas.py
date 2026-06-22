import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import requiere_roles
from app.models.enums import RolUsuario
from app.models.matricula import Matricula
from app.schemas.matricula import MatriculaCreate, MatriculaRead, MatriculaUpdate

router = APIRouter(
    prefix="/matriculas", tags=["Matrículas"], dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)


@router.get("/", response_model=list[MatriculaRead])
def listar_matriculas(
    grupo_id: uuid.UUID | None = None, anio_escolar_id: uuid.UUID | None = None, db: Session = Depends(get_db)
):
    query = db.query(Matricula)
    if grupo_id:
        query = query.filter(Matricula.grupo_id == grupo_id)
    if anio_escolar_id:
        query = query.filter(Matricula.anio_escolar_id == anio_escolar_id)
    return query.all()


@router.post("/", response_model=MatriculaRead, status_code=status.HTTP_201_CREATED)
def crear_matricula(datos: MatriculaCreate, db: Session = Depends(get_db)):
    matricula = Matricula(**datos.model_dump())
    db.add(matricula)
    db.commit()
    db.refresh(matricula)
    return matricula


@router.put("/{matricula_id}", response_model=MatriculaRead)
def actualizar_matricula(matricula_id: uuid.UUID, datos: MatriculaUpdate, db: Session = Depends(get_db)):
    matricula = db.get(Matricula, matricula_id)
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula no encontrada")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(matricula, campo, valor)
    db.commit()
    db.refresh(matricula)
    return matricula
