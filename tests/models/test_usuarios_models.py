import pytest
from sqlalchemy.exc import IntegrityError
from app.models.usuarios import Usuarios, load_user

def test_creacion_usuarios(test_db):
    """
    Prueba 1:Verifica la creación y guardado exitoso de un usuario.
    """

    usuario = Usuarios(
        nombre_usuario="Usuario de Prueba",
        correo_institucional="test@correo.com",
        rol="admin",
        foto_perfil="foto.png"
    )
    test_db.session.add(usuario)
    test_db.session.commit()

    usuario_guardado = Usuarios.query.filter_by(correo_institucional="test@correo.com").first()

    # Comprobar existencia del usuario
    assert usuario_guardado is not None
    assert usuario_guardado.nombre_usuario == "Usuario de Prueba"
    assert usuario_guardado.rol == "admin"
    assert usuario_guardado.id_usuario == usuario.id_usuario

    # Verificar get_id
    assert usuario.get_id() == str(usuario.id_usuario)


    loaded_user = load_user(str(usuario.id_usuario))

    assert loaded_user.id_usuario == usuario.id_usuario
    assert loaded_user.nombre_usuario == "Usuario de Prueba"

    