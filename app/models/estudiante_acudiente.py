import uuid

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Parentesco


class EstudianteAcudiente(Base):
    __tablename__ = "estudiantes_acudientes"
    __table_args__ = (UniqueConstraint("estudiante_id", "acudiente_id", name="uq_estudiante_acudiente"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("estudiantes.id"), nullable=False)
    acudiente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    parentesco: Mapped[Parentesco] = mapped_column(SAEnum(Parentesco, name="parentesco"), nullable=False)
    es_contacto_principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    estudiante = relationship("Estudiante", back_populates="acudientes")
    acudiente = relationship("Usuario", back_populates="vinculos_estudiantes")
