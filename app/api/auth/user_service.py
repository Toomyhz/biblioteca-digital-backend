from app.models.usuarios import Usuarios
from app.extensions import db
from sqlalchemy import select

def buscar_o_crear_usuario(claims):
    email = claims.get("email")
    stmt = select(Usuarios).where(Usuarios.correo_institucional == email)
    user = db.session.execute(stmt).scalar_one_or_none()
    if not user:
        # Crear nuevo usuario
        user = Usuarios(
            correo_institucional=claims.get("email"),
            nombre_usuario=claims.get("name"),
            foto_perfil=claims.get("picture"),
            rol="usuario"  # Rol por defecto
        )
        db.session.add(user)
    else:
        # Actualizar datos existentes
        user.nombre_usuario = claims.get("name")
        user.foto_perfil = claims.get("picture")
    db.session.commit()
    return user