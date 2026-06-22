"""python -m scripts.poblar_estudiantes"""
import random
import requests
from datetime import date, timedelta

BASE = "http://localhost:8000"
ANIO_ID = "be43b0d5-0add-4c40-a768-c25b14bda695"

GRUPOS = [
    {"id": "eced5f4a-0fb9-49aa-b8c5-4192bbaed956", "nombre": "Materno",      "nivel": "PRE-ESCOLAR", "cantidad": 8,  "edad_min": 3, "edad_max": 4},
    {"id": "95f74283-9944-4596-b259-aa2556ba8780", "nombre": "Kínder",       "nivel": "PRE-ESCOLAR", "cantidad": 9,  "edad_min": 4, "edad_max": 5},
    {"id": "d605835f-0c12-4d8f-84e7-8035be3641eb", "nombre": "Preparatoria", "nivel": "PRE-ESCOLAR", "cantidad": 9,  "edad_min": 5, "edad_max": 6},
    {"id": "8fdd522f-a39e-4997-ad95-5e6680220074", "nombre": "1° Grado",     "nivel": "PRIMARIA",    "cantidad": 10, "edad_min": 6, "edad_max": 7},
    {"id": "7589c06c-3a30-4d28-85fa-355175b3f776", "nombre": "2° Grado",     "nivel": "PRIMARIA",    "cantidad": 10, "edad_min": 7, "edad_max": 8},
    {"id": "c42cdfeb-6a5b-421f-8c87-0bfaa5060774", "nombre": "3° Grado",     "nivel": "PRIMARIA",    "cantidad": 10, "edad_min": 8, "edad_max": 9},
    {"id": "64800fbf-b336-470d-9c1b-fedc4ec0f10e", "nombre": "4° Grado",     "nivel": "PRIMARIA",    "cantidad": 10, "edad_min": 9, "edad_max": 10},
    {"id": "3adf3d47-6abb-4ceb-ba3a-98ed5c93d94f", "nombre": "5° Grado",     "nivel": "PRIMARIA",    "cantidad": 9,  "edad_min": 10, "edad_max": 11},
    {"id": "48adc4f6-0e9c-4672-8355-057bc6f593c8", "nombre": "6° Grado",     "nivel": "PRIMARIA",    "cantidad": 9,  "edad_min": 11, "edad_max": 12},
    {"id": "cebcbc3a-92e0-43a4-a1a8-5012af1b4ee3", "nombre": "7° Año",       "nivel": "SECUNDARIA",  "cantidad": 10, "edad_min": 12, "edad_max": 13},
    {"id": "eb5271ab-efe0-4d14-b0f7-8e1fdbf09076", "nombre": "8° Año",       "nivel": "SECUNDARIA",  "cantidad": 10, "edad_min": 13, "edad_max": 14},
    {"id": "f812339b-f8b5-4814-bff4-20181a2058c2", "nombre": "9° Año",       "nivel": "SECUNDARIA",  "cantidad": 10, "edad_min": 14, "edad_max": 15},
    {"id": "70308127-ea89-491d-8d7d-565a16180e07", "nombre": "10° Año",      "nivel": "SECUNDARIA",  "cantidad": 10, "edad_min": 15, "edad_max": 16},
    {"id": "4039f535-15ee-4996-9972-661e291c4a92", "nombre": "11° Año",      "nivel": "SECUNDARIA",  "cantidad": 11, "edad_min": 16, "edad_max": 17},
]

NOMBRES_M = [
    "Santiago", "Mateo", "Sebastián", "Nicolás", "Alejandro", "Diego", "Andrés",
    "Carlos", "Felipe", "Miguel", "José", "Luis", "Ricardo", "Eduardo", "Fernando",
    "Gabriel", "Héctor", "Ignacio", "Javier", "Leonardo", "Manuel", "Óscar", "Pablo",
    "Rafael", "Samuel", "Tomás", "Víctor", "Adrián", "Bruno", "César", "Darío",
    "Emilio", "Francisco", "Gonzalo", "Hugo", "Iván", "Joaquín", "Lorenzo", "Marcos",
    "Orlando", "Patricio", "Rodrigo", "Sergio", "Ulises", "Valentín", "Ángel",
    "Bernardo", "Cristian", "David", "Ernesto",
]

NOMBRES_F = [
    "Sofía", "Valentina", "Isabella", "Camila", "Lucía", "Valeria", "Daniela",
    "Mariana", "Paula", "Andrea", "María", "Laura", "Fernanda", "Carolina", "Alejandra",
    "Gabriela", "Patricia", "Natalia", "Claudia", "Diana", "Elena", "Florencia",
    "Gloria", "Iris", "Jimena", "Karina", "Leticia", "Mónica", "Nadia", "Olivia",
    "Paola", "Rebeca", "Silvia", "Teresa", "Verónica", "Ximena", "Yolanda", "Alicia",
    "Beatriz", "Carmen", "Dolores", "Eva", "Fabiola", "Graciela", "Hortensia",
    "Ingrid", "Juliana", "Karen", "Liliana", "Miriam",
]

APELLIDOS = [
    "García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Reyes", "Morales",
    "Cruz", "Ortega", "Vargas", "Castillo", "Ramos", "Herrera", "Medina", "Aguilar",
    "Vega", "Jiménez", "Núñez", "Álvarez", "Ruiz", "Muñoz", "Rojas", "Ríos",
    "Mendoza", "Chávez", "Delgado", "Fuentes", "Espinoza", "Salazar", "Cabrera",
    "Gutiérrez", "Luna", "Lara", "Campos", "Paredes", "Santana", "Sandoval",
    "Blanco", "Cárdenas", "Guerrero", "Mora", "Bernal", "Acosta", "Bravo",
    "Contreras", "Domínguez", "Estrada",
]


def fecha_nacimiento(edad_min: int, edad_max: int) -> str:
    edad_dias = random.randint(edad_min * 365, edad_max * 365)
    nacimiento = date(2026, 3, 1) - timedelta(days=edad_dias)
    return nacimiento.isoformat()


def nombre_completo() -> tuple[str, str]:
    genero = random.choice(["M", "F"])
    nombre = random.choice(NOMBRES_M if genero == "M" else NOMBRES_F)
    ap1 = random.choice(APELLIDOS)
    ap2 = random.choice(APELLIDOS)
    return f"{nombre} {ap1} {ap2}", genero


def main():
    # Login
    resp = requests.post(f"{BASE}/auth/login", data={
        "username": "admin@bemantis.com",
        "password": "Admin1234!",
    })
    resp.raise_for_status()
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    total_creados = 0
    nombres_usados = set()

    for grupo in GRUPOS:
        print(f"\n[{grupo['nivel']}] {grupo['nombre']} — {grupo['cantidad']} estudiantes")

        for i in range(grupo["cantidad"]):
            # Nombre único
            while True:
                nombre, genero = nombre_completo()
                if nombre not in nombres_usados:
                    nombres_usados.add(nombre)
                    break

            # Crear estudiante
            r = requests.post(f"{BASE}/estudiantes/", headers=headers, json={
                "nombre_completo": nombre,
                "fecha_nacimiento": fecha_nacimiento(grupo["edad_min"], grupo["edad_max"]),
                "genero": genero,
            })
            r.raise_for_status()
            estudiante_id = r.json()["id"]

            # Matricular en el grupo
            r2 = requests.post(f"{BASE}/matriculas/", headers=headers, json={
                "estudiante_id": estudiante_id,
                "grupo_id": grupo["id"],
                "anio_escolar_id": ANIO_ID,
                "fecha_matricula": "2026-01-15",
            })
            r2.raise_for_status()

            total_creados += 1
            print(f"  {total_creados:3d}. {nombre} ({genero})")

    print(f"\n✓ {total_creados} estudiantes creados y matriculados.")


if __name__ == "__main__":
    main()
