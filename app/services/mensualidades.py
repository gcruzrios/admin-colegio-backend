import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cargo import Cargo
from app.models.enums import EstadoMatricula, TipoCargo
from app.models.matricula import Matricula


def generar_mensualidades(
    db: Session, anio_escolar_id: uuid.UUID, mes: int, monto: Decimal, fecha_vencimiento: date
) -> int:
    """Crea un cargo MENSUALIDAD para cada estudiante con matrícula activa en el año.
    Evita duplicar si ya existe un cargo para ese estudiante y ese mes."""
    matriculas_activas = (
        db.query(Matricula)
        .filter(Matricula.anio_escolar_id == anio_escolar_id, Matricula.estado == EstadoMatricula.ACTIVA)
        .all()
    )
    creados = 0
    for matricula in matriculas_activas:
        ya_existe = (
            db.query(Cargo)
            .filter(
                Cargo.estudiante_id == matricula.estudiante_id,
                Cargo.anio_escolar_id == anio_escolar_id,
                Cargo.tipo == TipoCargo.MENSUALIDAD,
                Cargo.mes_correspondiente == mes,
            )
            .first()
        )
        if ya_existe:
            continue
        db.add(
            Cargo(
                estudiante_id=matricula.estudiante_id,
                anio_escolar_id=anio_escolar_id,
                tipo=TipoCargo.MENSUALIDAD,
                descripcion=f"Mensualidad {mes:02d}",
                monto=monto,
                mes_correspondiente=mes,
                fecha_emision=date.today(),
                fecha_vencimiento=fecha_vencimiento,
            )
        )
        creados += 1
    db.commit()
    return creados
