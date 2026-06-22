"""python -m scripts.generar_mensualidades"""
import random
import requests
from datetime import date

BASE     = "http://localhost:8000"
ANIO_ID  = "be43b0d5-0add-4c40-a768-c25b14bda695"
MESES    = [2, 3, 4, 5]   # Feb → May
VENCIMIENTOS = {
    2: date(2026, 2, 28),
    3: date(2026, 3, 31),
    4: date(2026, 4, 30),
    5: date(2026, 5, 31),
}
MONTOS = {
    "PRE-ESCOLAR": 90_000,
    "PRIMARIA":   110_000,
    "SECUNDARIA": 130_000,
}
META = 305

# ─── login ────────────────────────────────────────────────────────────────────
resp = requests.post(f"{BASE}/auth/login", data={
    "username": "admin@bemantis.com", "password": "Admin1234!"
})
resp.raise_for_status()
HDR = {"Authorization": f"Bearer {resp.json()['access_token']}"}

# ─── grupos → nivel ───────────────────────────────────────────────────────────
grupos_raw = requests.get(
    f"{BASE}/grupos/",
    params={"anio_escolar_id": ANIO_ID},
    headers=HDR
).json()
nivel_por_grupo = {g["id"]: g["nivel"] for g in grupos_raw}

# ─── matrículas del año ───────────────────────────────────────────────────────
matriculas = requests.get(
    f"{BASE}/matriculas/",
    params={"anio_escolar_id": ANIO_ID},
    headers=HDR
).json()

# mapa estudiante_id → nivel
nivel_por_estudiante: dict[str, str] = {}
for m in matriculas:
    nivel = nivel_por_grupo.get(m["grupo_id"])
    if nivel:
        nivel_por_estudiante[m["estudiante_id"]] = nivel

estudiantes = list(nivel_por_estudiante.keys())
random.shuffle(estudiantes)
total = len(estudiantes)   # 135

# ─── distribuir meses para llegar exactamente a 305 ──────────────────────────
# 135 estudiantes × 2 meses = 270  →  faltan 35 más
# 35 estudiantes reciben 3 meses, el resto 2 meses
# 35×3 + 100×2 = 105 + 200 = 305 ✓
asignaciones: dict[str, list[int]] = {}
idx_3_meses = set(random.sample(range(total), 35))

for i, eid in enumerate(estudiantes):
    if i in idx_3_meses:
        asignaciones[eid] = MESES[:3]   # Feb, Mar, Abr
    else:
        asignaciones[eid] = MESES[:2]   # Feb, Mar

# ─── crear cargos ─────────────────────────────────────────────────────────────
creados  = 0
errores  = 0
resumen  = {"PRE-ESCOLAR": 0, "PRIMARIA": 0, "SECUNDARIA": 0}

print(f"{'#':>4}  {'Nivel':<12} {'Mes':<4}  {'Monto':>10}  Estado")
print("─" * 50)

for eid, meses in asignaciones.items():
    nivel = nivel_por_estudiante[eid]
    monto = MONTOS[nivel]

    for mes in meses:
        payload = {
            "estudiante_id":    eid,
            "anio_escolar_id":  ANIO_ID,
            "tipo":             "MENSUALIDAD",
            "descripcion":      f"Mensualidad {mes:02d}/2026",
            "monto":            monto,
            "mes_correspondiente": mes,
            "fecha_emision":    "2026-01-31",
            "fecha_vencimiento": VENCIMIENTOS[mes].isoformat(),
        }
        r = requests.post(f"{BASE}/cargos/", headers=HDR, json=payload)
        if r.ok:
            creados += 1
            resumen[nivel] += 1
            print(f"{creados:>4}.  {nivel:<12} {mes:<4}  {monto:>10,}  OK")
        else:
            errores += 1
            print(f"       ERROR mes={mes} estudiante={eid}: {r.text}")

# ─── resumen ──────────────────────────────────────────────────────────────────
print("\n" + "═" * 50)
print(f"  Cargos creados  : {creados}")
print(f"  Errores         : {errores}")
print(f"  PRE-ESCOLAR     : {resumen['PRE-ESCOLAR']:>3} cargos × ¢ 90,000")
print(f"  PRIMARIA        : {resumen['PRIMARIA']:>3} cargos × ¢110,000")
print(f"  SECUNDARIA      : {resumen['SECUNDARIA']:>3} cargos × ¢130,000")
total_col = (resumen["PRE-ESCOLAR"] * 90_000
           + resumen["PRIMARIA"]    * 110_000
           + resumen["SECUNDARIA"]  * 130_000)
print(f"  Total facturado : ¢{total_col:>14,}")
