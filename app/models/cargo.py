import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoCargo, TipoCargo


class Cargo(Base):
    __tablename__ = "cargos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estudiantes.id"), nullable=False)
    anio_escolar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("anios_escolares.id"), nullable=False)
    tipo: Mapped[TipoCargo] = mapped_column(SAEnum(TipoCargo, name="tipo_cargo"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    mes_correspondiente: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_emision: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[EstadoCargo] = mapped_column(
        SAEnum(EstadoCargo, name="estado_cargo"), default=EstadoCargo.PENDIENTE, nullable=False
    )

    estudiante = relationship("Estudiante", back_populates="cargos")
    anio_escolar = relationship("AnioEscolar", back_populates="cargos")
    pagos = relationship("Pago", back_populates="cargo")
