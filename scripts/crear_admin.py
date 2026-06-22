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
