"""python -m scripts.crear_profesores"""
import random
import requests

BASE = "http://localhost:8000"

PROFESORES = [
    {"nombre": "Carlos Eduardo Vega Mora",        "asignatura": "Matemáticas",         "genero": "M"},
    {"nombre": "Laura Patricia Solís Brenes",      "asignatura": "Español",              "genero": "F"},
    {"nombre": "Andrés Felipe Quirós Ulate",       "asignatura": "Ciencias",             "genero": "M"},
    {"nombre": "María José Arias Benavides",       "asignatura": "Estudios Sociales",    "genero": "F"},
    {"nombre": "Roberto Alonso Coto Jiménez",      "asignatura": "Inglés",               "genero": "M"},
    {"nombre": "Diana Marcela Rojas Vargas",       "asignatura": "Educación Física",     "genero": "F"},
    {"nombre": "Mauricio Esteban Mora Blanco",     "asignatura": "Artes Plásticas",      "genero": "M"},
    {"nombre": "Silvia Elena Vindas Castro",       "asignatura": "Música",               "genero": "F"},
    {"nombre": "Jorge Luis Porras Fallas",         "asignatura": "Religión",             "genero": "M"},
    {"nombre": "Adriana Cecilia Mena Picado",      "asignatura": "Informática",          "genero": "F"},
    {"nombre": "Diego Armando Chaves Monge",       "asignatura": "Química",              "genero": "M"},
    {"nombre": "Paola Vanessa Salas Núñez",        "asignatura": "Física",               "genero": "F"},
    {"nombre": "Gustavo Adolfo Méndez Ortiz",      "asignatura": "Biología",             "genero": "M"},
    {"nombre": "Carolina Isabel Chavarría Ruiz",   "asignatura": "Historia",             "genero": "F"},
    {"nombre": "Héctor Manuel Bolaños Segura",     "asignatura": "Geografía",            "genero": "M"},
    {"nombre": "Stephanie Lorena Badilla Cruz",    "asignatura": "Francés",              "genero": "F"},
    {"nombre": "Fabián Rodrigo Calvo Zamora",      "asignatura": "Contabilidad",         "genero": "M"},
    {"nombre": "Natalia Gabriela Espinoza Herrera","asignatura": "Orientación",          "genero": "F"},
    {"nombre": "Luis Ángel Umaña Córdoba",         "asignatura": "Filosofía",            "genero": "M"},
    {"nombre": "Mariela Fernanda Mora Jiménez",    "asignatura": "Psicología",           "genero": "F"},
    {"nombre": "Alfredo Enrique Solano Araya",     "asignatura": "Agricultura y Ecología","genero": "M"},
]


def generar_cedula(usadas: set) -> str:
    while True:
        d1 = random.randint(1, 9)
        d2 = random.randint(0, 1)
        resto = "".join(str(random.randint(0, 9)) for _ in range(7))
        cedula = f"{d1}{d2}{resto}"
        if cedula not in usadas:
            usadas.add(cedula)
            return cedula


def generar_telefono() -> str:
    prefijo = random.choice(["6", "7", "8"])
    resto = "".join(str(random.randint(0, 9)) for _ in range(7))
    return f"{prefijo}{resto}"


def email_desde_nombre(nombre: str, idx: int) -> str:
    partes = nombre.lower().split()
    first = partes[0]
    last = partes[-1]
    first = first.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ñ","n")
    last  = last.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ñ","n")
    return f"{first}.{last}{idx}@colegio.edu"


def main():
    resp = requests.post(f"{BASE}/auth/login", data={
        "username": "admin@bemantis.com",
        "password": "Admin1234!",
    })
    resp.raise_for_status()
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cedulas: set = set()
    ok = 0

    print(f"{'#':>3}  {'Nombre':<40} {'Cédula':<12} {'Asignatura'}")
    print("-" * 90)

    for idx, prof in enumerate(PROFESORES, start=1):
        cedula = generar_cedula(cedulas)
        email  = email_desde_nombre(prof["nombre"], idx)

        r = requests.post(f"{BASE}/usuarios/", headers=headers, json={
            "nombre_completo": prof["nombre"],
            "email":           email,
            "password":        "Profesor1234!",
            "rol":             "PROFESOR",
            "telefono":        generar_telefono(),
            "identificacion":  cedula,
            "asignatura":      prof["asignatura"],
        })

        if r.ok:
            ok += 1
            print(f"{ok:>3}.  {prof['nombre']:<40} {cedula:<12} {prof['asignatura']}")
        else:
            print(f"  ERROR [{prof['nombre']}]: {r.text}")

    print(f"\n✓ {ok} profesores creados. Contraseña por defecto: Profesor1234!")


if __name__ == "__main__":
    main()
