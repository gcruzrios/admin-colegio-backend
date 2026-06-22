import uuid
from datetime import date

from sqlalchemy import Boolean, Date, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Genero


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    identificacion: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    genero: Mapped[Genero | None] = mapped_column(SAEnum(Genero, name="genero"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    acudientes = relationship("EstudianteAcudiente", back_populates="estudiante")
    matriculas = relationship("Matricula", back_populates="estudiante")
    cargos = relationship("Cargo", back_populates="estudiante")
