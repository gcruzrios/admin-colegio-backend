import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import MetodoPago


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cargo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cargos.id"), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)
    metodo_pago: Mapped[MetodoPago] = mapped_column(SAEnum(MetodoPago, name="metodo_pago"), nullable=False)
    numero_recibo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    registrado_por_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(String(255), nullable=True)

    cargo = relationship("Cargo", back_populates="pagos")
    registrado_por = relationship("Usuario", back_populates="pagos_registrados")
