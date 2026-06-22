import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, requiere_roles
from app.models.enums import RolUsuario
from app.models.cargo import Cargo
from app.models.estudiante import Estudiante
from app.models.estudiante_acudiente import EstudianteAcudiente
from app.models.usuario import Usuario
from app.schemas.cargo import CargoCreate, CargoRead, GenerarMensualidadesRequest
from app.services.mensualidades import generar_mensualidades

router = APIRouter(prefix="/cargos", tags=["Cargos"])


@router.post(
    "/", response_model=CargoRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)
def crear_cargo(datos: CargoCreate, db: Session = Depends(get_db)):
    if not db.get(Estudiante, datos.estudiante_id):
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    cargo = Cargo(**datos.model_dump())
    db.add(cargo)
    db.commit()
    db.refresh(cargo)
    return cargo


@router.post("/generar-mensualidades", dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))])
def generar_mensualidades_endpoint(datos: GenerarMensualidadesRequest, db: Session = Depends(get_db)):
    creados = generar_mensualidades(db, datos.anio_escolar_id, datos.mes, datos.monto, datos.fecha_vencimiento)
    return {"cargos_creados": creados}


@router.get("/estudiante/{estudiante_id}", response_model=list[CargoRead])
def listar_cargos_de_estudiante(
    estudiante_id: uuid.UUID, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)
):
    if usuario_actual.rol == RolUsuario.PADRE:
        vinculo = (
            db.query(EstudianteAcudiente)
            .filter_by(estudiante_id=estudiante_id, acudiente_id=usuario_actual.id)
            .first()
        )
        if not vinculo:
            raise HTTPException(status_code=403, detail="No tienes acceso a este estudiante")
    return db.query(Cargo).filter(Cargo.estudiante_id == estudiante_id).order_by(Cargo.fecha_vencimiento).all()
