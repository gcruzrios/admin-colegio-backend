# Backend — Sistema Escolar (FastAPI + PostgreSQL)

Implementación completa de las 8 entidades del modelo de datos: `Usuario`, `AnioEscolar`, `Grupo`, `Estudiante`, `EstudianteAcudiente`, `Matricula`, `Cargo` y `Pago`. Incluye autenticación JWT con 3 roles (ADMIN, PROFESOR, PADRE), autorización por endpoint, y la lógica de negocio para generar mensualidades en lote y calcular el estado de cuenta de cada cargo.

Recomendación: usa Python 3.12 para este proyecto (FastAPI/SQLAlchemy 2.0 todavía tienen fricción con 3.14).

## Estructura del proyecto

```
backend/
  app/
    core/
      config.py
      database.py
      security.py
      deps.py
    models/
      __init__.py
      enums.py
      usuario.py
      anio_escolar.py
      grupo.py
      estudiante.py
      estudiante_acudiente.py
      matricula.py
      cargo.py
      pago.py
    schemas/
      auth.py
      usuario.py
      anio_escolar.py
      grupo.py
      estudiante.py
      estudiante_acudiente.py
      matricula.py
      cargo.py
      pago.py
    services/
      cargos.py
      mensualidades.py
    api/
      routers/
        auth.py
        usuarios.py
        estudiantes.py
        grupos.py
        anios_escolares.py
        acudientes.py
        matriculas.py
        cargos.py
        pagos.py
    main.py
  scripts/
    crear_admin.py
  alembic/
    env.py
  alembic.ini
  requirements.txt
  .env
```

Crea un archivo vacío `__init__.py` en `app/`, `app/core/`, `app/models/`, `app/schemas/`, `app/services/`, `app/api/` y `app/api/routers/` para que Python reconozca cada carpeta como paquete (no se repiten aquí por brevedad).

## Instalación

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### `requirements.txt`
```
fastapi>=0.115
uvicorn[standard]>=0.32
sqlalchemy>=2.0.36
psycopg2-binary>=2.9.10
alembic>=1.14
pydantic>=2.9
pydantic-settings>=2.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.12
python-dotenv>=1.0.1
```

#### `.env`
```
DATABASE_URL=postgresql://usuario:password@localhost:5432/colegio_db
SECRET_KEY=cambia-esto-por-una-clave-larga-y-aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

## Configuración base

#### `app/core/config.py`
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    class Config:
        env_file = ".env"


settings = Settings()
```

#### `app/core/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### `app/core/security.py`
```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
```

## Enumeraciones

#### `app/models/enums.py`
```python
import enum


class RolUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    PROFESOR = "PROFESOR"
    PADRE = "PADRE"


class TipoCargo(str, enum.Enum):
    MATRICULA = "MATRICULA"
    MENSUALIDAD = "MENSUALIDAD"
    MATERIAL = "MATERIAL"
    OTRO = "OTRO"


class EstadoCargo(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PARCIAL = "PARCIAL"
    PAGADO = "PAGADO"
    VENCIDO = "VENCIDO"
    ANULADO = "ANULADO"


class EstadoMatricula(str, enum.Enum):
    ACTIVA = "ACTIVA"
    RETIRADO = "RETIRADO"
    GRADUADO = "GRADUADO"
    TRASLADADO = "TRASLADADO"


class MetodoPago(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    SINPE_MOVIL = "SINPE_MOVIL"
    TARJETA = "TARJETA"
    CHEQUE = "CHEQUE"


class Parentesco(str, enum.Enum):
    MADRE = "MADRE"
    PADRE = "PADRE"
    TUTOR = "TUTOR"
    OTRO = "OTRO"


class Genero(str, enum.Enum):
    M = "M"
    F = "F"
    OTRO = "OTRO"
```

## Modelos (SQLAlchemy 2.0)

#### `app/models/usuario.py`
```python
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import RolUsuario


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(SAEnum(RolUsuario, name="rol_usuario"), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    grupos_dirigidos = relationship("Grupo", back_populates="profesor_guia")
    vinculos_estudiantes = relationship("EstudianteAcudiente", back_populates="acudiente")
    pagos_registrados = relationship("Pago", back_populates="registrado_por")
```

#### `app/models/anio_escolar.py`
```python
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnioEscolar(Base):
    __tablename__ = "anios_escolares"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    grupos = relationship("Grupo", back_populates="anio_escolar")
    matriculas = relationship("Matricula", back_populates="anio_escolar")
    cargos = relationship("Cargo", back_populates="anio_escolar")
```

#### `app/models/grupo.py`
```python
import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Grupo(Base):
    __tablename__ = "grupos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    nivel: Mapped[str] = mapped_column(String(50), nullable=False)
    anio_escolar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("anios_escolares.id"), nullable=False)
    profesor_guia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    capacidad_maxima: Mapped[int | None] = mapped_column(Integer, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    anio_escolar = relationship("AnioEscolar", back_populates="grupos")
    profesor_guia = relationship("Usuario", back_populates="grupos_dirigidos")
    matriculas = relationship("Matricula", back_populates="grupo")
```

#### `app/models/estudiante.py`
```python
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
```

#### `app/models/estudiante_acudiente.py`
```python
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
```

#### `app/models/matricula.py`
```python
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
```

#### `app/models/cargo.py`
```python
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
```

#### `app/models/pago.py`
```python
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
```

#### `app/models/__init__.py`
```python
from app.models.usuario import Usuario
from app.models.anio_escolar import AnioEscolar
from app.models.grupo import Grupo
from app.models.estudiante import Estudiante
from app.models.estudiante_acudiente import EstudianteAcudiente
from app.models.matricula import Matricula
from app.models.cargo import Cargo
from app.models.pago import Pago
```

## Esquemas (Pydantic)

#### `app/schemas/auth.py`
```python
from pydantic import BaseModel

from app.models.enums import RolUsuario


class Token(BaseModel):
    access_token: str
    token_type: str
    rol: RolUsuario
    nombre_completo: str
```

#### `app/schemas/usuario.py`
```python
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import RolUsuario


class UsuarioBase(BaseModel):
    nombre_completo: str
    email: EmailStr
    rol: RolUsuario
    telefono: str | None = None


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    nombre_completo: str | None = None
    telefono: str | None = None
    activo: bool | None = None


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    activo: bool
    created_at: datetime
```

#### `app/schemas/anio_escolar.py`
```python
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class AnioEscolarCreate(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    activo: bool = False


class AnioEscolarRead(AnioEscolarCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
```

#### `app/schemas/grupo.py`
```python
import uuid

from pydantic import BaseModel, ConfigDict


class GrupoBase(BaseModel):
    nombre: str
    nivel: str
    anio_escolar_id: uuid.UUID
    profesor_guia_id: uuid.UUID | None = None
    capacidad_maxima: int | None = None


class GrupoCreate(GrupoBase):
    pass


class GrupoUpdate(BaseModel):
    nombre: str | None = None
    nivel: str | None = None
    profesor_guia_id: uuid.UUID | None = None
    capacidad_maxima: int | None = None
    activo: bool | None = None


class GrupoRead(GrupoBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    activo: bool
```

#### `app/schemas/estudiante.py`
```python
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import Genero


class EstudianteBase(BaseModel):
    nombre_completo: str
    identificacion: str | None = None
    fecha_nacimiento: date
    genero: Genero | None = None


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(BaseModel):
    nombre_completo: str | None = None
    identificacion: str | None = None
    fecha_nacimiento: date | None = None
    genero: Genero | None = None
    activo: bool | None = None


class EstudianteRead(EstudianteBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    activo: bool
```

#### `app/schemas/estudiante_acudiente.py`
```python
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import Parentesco


class EstudianteAcudienteCreate(BaseModel):
    estudiante_id: uuid.UUID
    acudiente_id: uuid.UUID
    parentesco: Parentesco
    es_contacto_principal: bool = False


class EstudianteAcudienteRead(EstudianteAcudienteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
```

#### `app/schemas/matricula.py`
```python
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import EstadoMatricula


class MatriculaCreate(BaseModel):
    estudiante_id: uuid.UUID
    grupo_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    fecha_matricula: date


class MatriculaUpdate(BaseModel):
    estado: EstadoMatricula | None = None
    grupo_id: uuid.UUID | None = None


class MatriculaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    estudiante_id: uuid.UUID
    grupo_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    fecha_matricula: date
    estado: EstadoMatricula
```

#### `app/schemas/cargo.py`
```python
import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import EstadoCargo, TipoCargo


class CargoCreate(BaseModel):
    estudiante_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    tipo: TipoCargo
    descripcion: str
    monto: Decimal
    mes_correspondiente: int | None = None
    fecha_emision: date
    fecha_vencimiento: date


class CargoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    estudiante_id: uuid.UUID
    anio_escolar_id: uuid.UUID
    tipo: TipoCargo
    descripcion: str
    monto: Decimal
    mes_correspondiente: int | None
    fecha_emision: date
    fecha_vencimiento: date
    estado: EstadoCargo


class GenerarMensualidadesRequest(BaseModel):
    anio_escolar_id: uuid.UUID
    mes: int
    monto: Decimal
    fecha_vencimiento: date
```

#### `app/schemas/pago.py`
```python
import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import MetodoPago


class PagoCreate(BaseModel):
    cargo_id: uuid.UUID
    monto: Decimal
    fecha_pago: date
    metodo_pago: MetodoPago
    observaciones: str | None = None


class PagoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    cargo_id: uuid.UUID
    monto: Decimal
    fecha_pago: date
    metodo_pago: MetodoPago
    numero_recibo: str
    observaciones: str | None
```

## Autenticación y autorización por rol

#### `app/core/deps.py`
```python
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.enums import RolUsuario
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    usuario = db.get(Usuario, uuid.UUID(payload.get("sub")))
    if usuario is None or not usuario.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo")
    return usuario


def requiere_roles(*roles_permitidos: RolUsuario):
    def verificador(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para esta acción")
        return usuario

    return verificador
```

## Lógica de negocio

#### `app/services/cargos.py`
```python
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cargo import Cargo
from app.models.enums import EstadoCargo


def actualizar_estado_cargo(db: Session, cargo: Cargo) -> None:
    """Recalcula el estado de un cargo según la suma de sus pagos."""
    total_pagado = sum((pago.monto for pago in cargo.pagos), Decimal("0"))
    if total_pagado <= 0:
        cargo.estado = EstadoCargo.PENDIENTE
    elif total_pagado < cargo.monto:
        cargo.estado = EstadoCargo.PARCIAL
    else:
        cargo.estado = EstadoCargo.PAGADO
    db.commit()
```

#### `app/services/mensualidades.py`
```python
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
```

## Endpoints

#### `app/api/routers/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.usuario import Usuario
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    if not usuario.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
    access_token = create_access_token({"sub": str(usuario.id), "rol": usuario.rol.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": usuario.rol,
        "nombre_completo": usuario.nombre_completo,
    }
```

#### `app/api/routers/usuarios.py`
```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import requiere_roles
from app.core.security import hash_password
from app.models.enums import RolUsuario
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(
    prefix="/usuarios", tags=["Usuarios"], dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)


@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(rol: RolUsuario | None = None, db: Session = Depends(get_db)):
    query = db.query(Usuario)
    if rol:
        query = query.filter(Usuario.rol == rol)
    return query.order_by(Usuario.nombre_completo).all()


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")
    usuario = Usuario(
        nombre_completo=datos.nombre_completo,
        email=datos.email,
        password_hash=hash_password(datos.password),
        rol=datos.rol,
        telefono=datos.telefono,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(usuario_id: uuid.UUID, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = False
    db.commit()
```

#### `app/api/routers/estudiantes.py`
```python
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
```

#### `app/api/routers/grupos.py`
```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, requiere_roles
from app.models.enums import RolUsuario
from app.models.grupo import Grupo
from app.models.usuario import Usuario
from app.schemas.grupo import GrupoCreate, GrupoRead, GrupoUpdate

router = APIRouter(prefix="/grupos", tags=["Grupos"])


@router.get("/", response_model=list[GrupoRead])
def listar_grupos(anio_escolar_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(Grupo).filter(Grupo.activo == True)  # noqa: E712
    if anio_escolar_id:
        query = query.filter(Grupo.anio_escolar_id == anio_escolar_id)
    return query.order_by(Grupo.nombre).all()


@router.get("/mi-grupo", response_model=list[GrupoRead], dependencies=[Depends(requiere_roles(RolUsuario.PROFESOR))])
def mi_grupo(db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    return db.query(Grupo).filter(Grupo.profesor_guia_id == usuario_actual.id, Grupo.activo == True).all()  # noqa: E712


@router.post(
    "/", response_model=GrupoRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)
def crear_grupo(datos: GrupoCreate, db: Session = Depends(get_db)):
    grupo = Grupo(**datos.model_dump())
    db.add(grupo)
    db.commit()
    db.refresh(grupo)
    return grupo


@router.put("/{grupo_id}", response_model=GrupoRead, dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))])
def actualizar_grupo(grupo_id: uuid.UUID, datos: GrupoUpdate, db: Session = Depends(get_db)):
    grupo = db.get(Grupo, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(grupo, campo, valor)
    db.commit()
    db.refresh(grupo)
    return grupo
```

#### `app/api/routers/anios_escolares.py`
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import requiere_roles
from app.models.anio_escolar import AnioEscolar
from app.models.enums import RolUsuario
from app.schemas.anio_escolar import AnioEscolarCreate, AnioEscolarRead

router = APIRouter(prefix="/anios-escolares", tags=["Años escolares"])


@router.get("/", response_model=list[AnioEscolarRead])
def listar_anios(db: Session = Depends(get_db)):
    return db.query(AnioEscolar).order_by(AnioEscolar.nombre.desc()).all()


@router.post(
    "/",
    response_model=AnioEscolarRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))],
)
def crear_anio_escolar(datos: AnioEscolarCreate, db: Session = Depends(get_db)):
    if datos.activo:
        db.query(AnioEscolar).update({AnioEscolar.activo: False})
    anio = AnioEscolar(**datos.model_dump())
    db.add(anio)
    db.commit()
    db.refresh(anio)
    return anio
```

#### `app/api/routers/acudientes.py`
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import requiere_roles
from app.models.enums import RolUsuario
from app.models.estudiante_acudiente import EstudianteAcudiente
from app.schemas.estudiante_acudiente import EstudianteAcudienteCreate, EstudianteAcudienteRead

router = APIRouter(
    prefix="/acudientes", tags=["Acudientes"], dependencies=[Depends(requiere_roles(RolUsuario.ADMIN))]
)


@router.post("/vincular", response_model=EstudianteAcudienteRead, status_code=status.HTTP_201_CREATED)
def vincular_acudiente(datos: EstudianteAcudienteCreate, db: Session = Depends(get_db)):
    vinculo = EstudianteAcudiente(**datos.model_dump())
    db.add(vinculo)
    db.commit()
    db.refresh(vinculo)
    return vinculo
```

#### `app/api/routers/matriculas.py`
```python
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
```

#### `app/api/routers/cargos.py`
```python
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
```

#### `app/api/routers/pagos.py`
```python
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
```

## `app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    acudientes,
    anios_escolares,
    auth,
    cargos,
    estudiantes,
    grupos,
    matriculas,
    pagos,
    usuarios,
)

app = FastAPI(title="Sistema Escolar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(estudiantes.router)
app.include_router(grupos.router)
app.include_router(anios_escolares.router)
app.include_router(acudientes.router)
app.include_router(matriculas.router)
app.include_router(cargos.router)
app.include_router(pagos.router)


@app.get("/")
def root():
    return {"mensaje": "Sistema Escolar API activo"}
```

## Migraciones con Alembic

```bash
alembic init alembic
```

Edita `alembic/env.py` agregando, antes de `run_migrations_offline()`:

```python
from app.core.database import Base
from app.core.config import settings
import app.models  # noqa: F401  — registra todos los modelos en Base.metadata

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.database_url)
```

Genera y aplica la primera migración (esto crea todas las tablas en PostgreSQL):

```bash
alembic revision --autogenerate -m "modelo inicial"
alembic upgrade head
```

## Primer usuario administrador

#### `scripts/crear_admin.py`
```python
"""Ejecutar una sola vez: python -m scripts.crear_admin"""
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.enums import RolUsuario
from app.models.usuario import Usuario


def main():
    db = SessionLocal()
    email = input("Correo del administrador: ")
    password = input("Contraseña: ")
    nombre = input("Nombre completo: ")
    if db.query(Usuario).filter(Usuario.email == email).first():
        print("Ya existe un usuario con ese correo")
        return
    db.add(
        Usuario(
            nombre_completo=nombre,
            email=email,
            password_hash=hash_password(password),
            rol=RolUsuario.ADMIN,
        )
    )
    db.commit()
    print(f"Administrador creado: {email}")


if __name__ == "__main__":
    main()
```

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`.
