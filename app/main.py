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
