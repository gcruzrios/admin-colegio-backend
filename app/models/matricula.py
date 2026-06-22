import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoMatricula


class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estudiantes.id"), nullable=False)
    grupo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False)
    anio_escolar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("anios_escolares.id"), nullable=False)
    fecha_matricula: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[EstadoMatricula] = mapped_column(
        SAEnum(EstadoMatricula, name="estado_matricula"), default=EstadoMatricula.ACTIVA, nullable=False
    )

    estudiante = relationship("Estudiante", back_populates="matriculas")
    grupo = relationship("Grupo", back_populates="matriculas")
    anio_escolar = relationship("AnioEscolar", back_populates="matriculas")
