import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, requiere_roles
from app.models.cargo import Cargo
from app.models.enums import RolUsuario
from app.models.pago import Pago
from app.models.usuario import Usuario
from app.schemas.pago import PagoCreate, PagoRead
from app.services.cargos import actualizar_estado_cargo

router = APIRouter(prefix="/pagos", tags=["Pagos"])


def generar_numero_recibo(db: Session) -> str:
    total = db.query(Pago).count() + 1
    return f"REC-{total:06d}"


@router.post(
    "/", response_model=PagoRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)
def registrar_pago(datos: PagoCreate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    cargo = db.get(Cargo, datos.cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    pago = Pago(
        **datos.model_dump(),
        numero_recibo=generar_numero_recibo(db),
        registrado_por_id=usuario_actual.id,
    )
    db.add(pago)
    db.commit()
    db.refresh(cargo)
    actualizar_estado_cargo(db, cargo)
    db.refresh(pago)
    return pago


@router.get("/cargo/{cargo_id}", response_model=list[PagoRead])
def listar_pagos_de_cargo(cargo_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Pago).filter(Pago.cargo_id == cargo_id).order_by(Pago.fecha_pago).all()
