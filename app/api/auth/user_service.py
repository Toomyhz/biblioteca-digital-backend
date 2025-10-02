from app.models.usuarios import Usuarios
from app import db

def buscar_o_crear_usuario(claims):
    email = claims.get("email")
    user = Usuarios.query.filter_by(correo_institucional=email).first()
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