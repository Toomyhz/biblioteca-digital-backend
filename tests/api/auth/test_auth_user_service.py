from app.api.auth.user_service import buscar_o_crear_usuario
from app.models.usuarios import Usuarios
from sqlalchemy import select

def test_crear_nuevo_usuario(test_db):
    """
    Verifica que un usuario nuevo sea creado correctamente en la base de datos cuando no existe previamente.
    """
    # Datos simulados que vendrían del proveedor de Oauth

    mock_claims = {
        "email": "tomas.hernandez@umce.cl",
        "name":"Tomás Hernández",
        "picture": "http://example.com/foto_nueva.jpg"
    }
    user_creado = buscar_o_crear_usuario(mock_claims)
    assert user_creado is not None
    assert user_creado.correo_institucional == "tomas.hernandez@umce.cl"
    assert user_creado.nombre_usuario == "Tomás Hernández"
    assert user_creado.rol == "usuario" 

    # Verificar directamente en la base de datos:
    stmt = select(Usuarios).where(Usuarios.correo_institucional == "tomas.hernandez@umce.cl")
    user_en_db = test_db.session.execute(stmt).scalar_one()

    assert user_en_db.id_usuario == user_creado.id_usuario
    assert user_en_db.nombre_usuario == "Tomás Hernández"

def test_actualizar_usuario(test_db):
    """
    Verifica que a un usuario existente se actualizan datos.
    """
    # Primero se crea el usuario directo en la base de datos simulando un registro/logeo en otra sesion.
    
    usuario_original = Usuarios(
        correo_institucional = "tomas.hernandez@umce.cl", 
        nombre_usuario = "Tomás Hernández",
        rol = "usuario" ,
        foto_perfil = "http://example.com/foto_nueva.jpg"
    )
    test_db.session.add(usuario_original)
    test_db.session.commit()

    id_original = usuario_original.id_usuario
    # Simulamos nueva llamada correspondiente a otro inicio de sesión.
    mock_claims_actualizados = {
        "email":"tomas.hernandez@umce.cl",
        "name": "TOMAS HERNANDEZ MANZOR",
        "picture":"mi_nueva_foto.png"
    }
    user_modificado = buscar_o_crear_usuario(mock_claims_actualizados)

    # Verificamos que no se creo un nuevo usuario
    assert user_modificado.id_usuario == id_original
    # Verificamos que los datos se actualizaron correctamente.
    assert user_modificado.nombre_usuario == "TOMAS HERNANDEZ MANZOR"
    assert user_modificado.foto_perfil == "mi_nueva_foto.png"

    # Verificamos que los datos que no deberían cambiar, no cambiaron
    assert user_modificado.rol == "usuario"

    # 4. (Mejora) Verificar que el número total de usuarios en la BD sigue siendo 1
    total_users = test_db.session.execute(select(test_db.func.count(Usuarios.id_usuario))).scalar()
    assert total_users == 1
