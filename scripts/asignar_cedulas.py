"""python -m scripts.asignar_cedulas"""
import random
import requests

BASE = "http://localhost:8000"


def generar_cedula(usadas: set) -> str:
    while True:
        d1 = random.randint(1, 9)
        d2 = random.randint(0, 1)
        d3 = random.randint(0, 9)
        d4 = random.randint(0, 9)
        d5 = random.randint(0, 9)
        d6 = random.randint(0, 9)
        d7 = random.randint(0, 9)
        d8 = random.randint(0, 9)
        d9 = random.randint(0, 9)
        cedula = f"{d1}{d2}{d3}{d4}{d5}{d6}{d7}{d8}{d9}"
        if cedula not in usadas:
            usadas.add(cedula)
            return cedula


def main():
    resp = requests.post(f"{BASE}/auth/login", data={
        "username": "admin@bemantis.com",
        "password": "Admin1234!",
    })
    resp.raise_for_status()
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    estudiantes = requests.get(f"{BASE}/estudiantes/", headers=headers)
    estudiantes.raise_for_status()
    lista = estudiantes.json()
    print(f"Estudiantes encontrados: {len(lista)}\n")

    cedulas_usadas: set = set()
    ok = 0
    errores = 0

    for est in sorted(lista, key=lambda e: e["nombre_completo"]):
        cedula = generar_cedula(cedulas_usadas)
        r = requests.put(f"{BASE}/estudiantes/{est['id']}", headers=headers, json={
            "identificacion": cedula
        })
        if r.ok:
            ok += 1
            print(f"  {ok:3d}. {est['nombre_completo']:<35} → {cedula}")
        else:
            errores += 1
            print(f"  ERROR {est['nombre_completo']}: {r.text}")

    print(f"\n✓ {ok} cédulas asignadas  |  ✗ {errores} errores")


if __name__ == "__main__":
    main()
