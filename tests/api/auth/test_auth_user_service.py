from app.api.auth.user_service import buscar_o_crear_usuario
from app.models.usuarios import Usuarios
from sqlalchemy import select

def test_crear_nuevo_usuario(mocker):
    """
    Verifica que un usuario nuevo sea creado correctamente en la base de datos cuando no existe previamente.
    """
    # Datos simulados que vendrían del proveedor de Oauth

    mock_claims = {
        "email": "tomas.hernandez@umce.cl",
        "name":"Tomás Hernández",
        "picture": "http://example.com/foto_nueva.jpg"
    }
    mock_db_execute = mocker.patch(
        "app.api.auth.user_service.db.session.execute",
    )
    mock_db_execute.return_value.scalar_one_or_none.return_value = None  # Simula que no existe el usuario
    mock_db_add = mocker.patch(
        "app.api.auth.user_service.db.session.add",
    )
    mock_db_commit = mocker.patch(
        "app.api.auth.user_service.db.session.commit",
    )
    user_creado = buscar_o_crear_usuario(mock_claims)
    assert user_creado is not None
    assert user_creado.correo_institucional == "tomas.hernandez@umce.cl"
    assert user_creado.nombre_usuario == "Tomás Hernández"
    assert user_creado.rol == "usuario" 

    mock_db_add.assert_called_once()
    mock_db_commit.assert_called_once()


def test_actualizar_usuario(mocker):
    """
    Verifica que a un usuario existente se actualizan datos.
    """
    # Primero se crea el usuario directo en la base de datos simulando un registro/logeo en otra sesion.
    mock_usuario_existente = Usuarios(
        id_usuario=1,
        correo_institucional="tomas.hernandez@umce.cl",
        nombre_usuario="Tomás Hernández",
        foto_perfil="mi_foto.png",
        rol="usuario"
    )

    mock_db_execute = mocker.patch(
        "app.api.auth.user_service.db.session.execute",
    )
    mock_db_execute.return_value.scalar_one_or_none.return_value =  mock_usuario_existente

    mock_db_commit = mocker.patch(
        "app.api.auth.user_service.db.session.commit",
    )

    # Simulamos nueva llamada correspondiente a otro inicio de sesión.
    mock_claims_actualizados = {
        "email":"tomas.hernandez@umce.cl",
        "name": "TOMAS HERNANDEZ MANZOR",
        "picture":"mi_nueva_foto.png"
    }
    user_modificado = buscar_o_crear_usuario(mock_claims_actualizados)

    # Verificamos que no se creo un nuevo usuario
    assert user_modificado.id_usuario == 1

    # Verificamos que los datos se actualizaron correctamente.
    assert user_modificado.nombre_usuario == "TOMAS HERNANDEZ MANZOR"
    assert user_modificado.foto_perfil == "mi_nueva_foto.png"

    # Verificamos que los datos que no deberían cambiar, no cambiaron
    assert user_modificado.rol == "usuario"

    mock_db_commit.assert_called_once()

