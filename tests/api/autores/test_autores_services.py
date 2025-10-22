from app.api.autores.services import agregar_autor_service, listar_autores_service, actualizar_autor_service, eliminar_autor_service
from app.models.autores import Autores
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock

def test_agregar_autor_service(app,test_db):
    with app.app_context():
        nueva_data = {
            "new_nombre":"Bruce Wayne",
            "new_nacionalidad":"Estadounidense"
        }
        diccionario, estado = agregar_autor_service(nueva_data)

        # Se valida el código de estado y el diccionario de retorno
        assert estado == 201
        assert diccionario["mensaje"] == "Autor agregado correctamente"
        assert diccionario["autor"]["nombre_completo"] == "Bruce Wayne"
        assert diccionario["autor"]["nacionalidad"] == "Estadounidense"

        # Se guarda el ID para ir a buscar a DB
        id_autor_creado = diccionario["autor"]["id_autor"]

        # Guardamos el registro del autor para compararlo con el del retorno
        autor_en_db = test_db.session.get(Autores,id_autor_creado)
        assert autor_en_db.nombre_completo == nueva_data["new_nombre"]
        assert autor_en_db.nacionalidad == nueva_data["new_nacionalidad"]

def test_agregar_autor_service_error_sin_nombre():
    nueva_data = {
        "new_nacionalidad":"Estadounidense"
    }
    diccionario, estado = agregar_autor_service(nueva_data)

    # Se valida el código de estado y el diccionario de retorno
    assert estado == 400
    assert diccionario["error"] == "El nombre del autor es obligatorio"


def test_agregar_autor_service_error_base_datos(app,mocker,test_db):
    with app.app_context():
        nueva_data = {
            "new_nombre":"Bruce Wayne",
            "new_nacionalidad":"Estadounidense"
        }
        mock_commit = mocker.patch("app.api.autores.services.db.session.commit")
        mock_commit.side_effect = SQLAlchemyError("Fallo de conexión simulado")
        mock_rollback = mocker.patch("app.api.autores.services.db.session.rollback")

        diccionario, estado = agregar_autor_service(nueva_data)

        # El rollback fue llamado una vez
        mock_rollback.assert_called_once()

        # Se valida el código de estado y el diccionario de retorno
        assert estado == 500
        assert diccionario["error"] == "Error al crear autor: Fallo de conexión simulado"

def test_listar_autores_services_error_db(app, mocker):
    """
    Prueba unitaria que verifica el manejo de errores de la base de datos
    de forma aislada y con el contexto de aplicación correcto.
    """
    # 1. Empuja el contexto de la aplicación. ¡Ahora la "oficina" está abierta!
    with app.app_context():
        # --- ARRANGE ---
        # 2. Ahora que la oficina está abierta, el mocker puede encontrar los objetos a parchear.
        mock_query = mocker.patch("app.api.autores.services.Autores")
        mock_query.query.order_by.return_value.all.side_effect = SQLAlchemyError("Fallo de conexión simulado")
        
        mock_rollback = mocker.patch("app.api.autores.services.db.session.rollback")

        # --- ACT ---
        respuesta, estado = listar_autores_service()

        # --- ASSERT ---
        # Como el RuntimeError ya no ocurre, el flujo continúa:
        # 1. Se lanza el SQLAlchemyError simulado.
        # 2. El bloque `except` se activa.
        # 3. Se llama a db.session.rollback().
        # Por lo tanto, esta aserción ahora pasará.
        mock_rollback.assert_called_once()
        
        assert estado == 500
        
        # Este assert también pasará, ya que la excepción capturada será la que simulaste.
        # (Aunque es mejor práctica validar un mensaje genérico).
        assert "Fallo de conexión simulado" in respuesta["error"]

def test_actualizar_autor_service_sin_autor(app,mocker):
    with app.app_context():
        mock_autores = mocker.patch("app.api.autores.services.Autores")
        mock_autores.query.get.return_value = None
        test_data = {
            "edit_nombre":"Alonso"
        }
        response, status = actualizar_autor_service(1,test_data)

        assert response["error"] == "Autor no encontrado"
        assert status == 404

def test_actualizar_autor_service_sin_nombre_completo(app,mocker):
    with app.app_context():
        mock_autor_existente = MagicMock()
        mock_autor_existente.id_autor = 1
        mock_autor_existente.nombre_completo = "Daniel Cabello"
        mock_autor_existente.nacionalidad = "Chileno"
        mock_autor_existente.slug_autor = "daniel-cabello-1"


        mock_autores = mocker.patch("app.api.autores.services.Autores")
        mock_autores.query.get.return_value = mock_autor_existente
        test_data = {
            "edit_nacionalidad":"Peruano"
        }
        
        
        response, status = actualizar_autor_service(1,test_data)

        assert response["error"] == "El nombre del autor es obligatorio"
        assert status == 400

def test_actualizar_autor_service_exitoso(app,mocker):
    with app.app_context():
        mock_autor_existente = MagicMock()
        mock_autor_existente.id_autor = 1
        mock_autor_existente.nombre_completo = "Daniel Cabello"
        mock_autor_existente.nacionalidad = "Chileno"
        mock_autor_existente.slug_autor = "daniel-cabello-1"

        mock_autor_existente.to_dict.return_value = {
            "id_autor": 1,
            "nombre_completo": "Danielo Cabellera",
            "nacionalidad": "Peruano",
            "slug_autor": "danielo-cabellera-1" 
        }


        mock_autores = mocker.patch("app.api.autores.services.Autores")
        mock_autores.query.get.return_value = mock_autor_existente
        test_data = {
            "edit_nombre":"Danielo Cabellera",
            "edit_nacionalidad":"Peruano"
        }
        
        mock_slug = mocker.patch("app.api.autores.services.generar_slug")
        mock_slug.return_value = "danielo-cabellera-1"

        mock_commit = mocker.patch("app.api.autores.services.db.session.commit")
        
        response, status = actualizar_autor_service(1,test_data)

        mock_commit.assert_called_once()
        assert status == 201
        assert response["mensaje"] == 'Autor actualizado correctamente'
        assert response["autor"]["nombre_completo"] == test_data["edit_nombre"]

def test_actualizar_autor_service_error_db(app,mocker):
    with app.app_context():
        mock_autor_existente = MagicMock()
        mock_autor_existente.id_autor = 1
        mock_autor_existente.nombre_completo = "Daniel Cabello"
        mock_autor_existente.nacionalidad = "Chileno"
        mock_autor_existente.slug_autor = "daniel-cabello-1"

        mock_autor_existente.to_dict.return_value = {
            "id_autor": 1,
            "nombre_completo": "Danielo Cabellera",
            "nacionalidad": "Peruano",
            "slug_autor": "danielo-cabellera-1" 
        }


        mock_autores = mocker.patch("app.api.autores.services.Autores")
        mock_autores.query.get.return_value = mock_autor_existente
        test_data = {
            "edit_nombre":"Danielo Cabellera",
            "edit_nacionalidad":"Peruano"
        }
        
        mock_slug = mocker.patch("app.api.autores.services.generar_slug")
        mock_slug.return_value = "danielo-cabellera-1"

        mock_commit = mocker.patch("app.api.autores.services.db.session.commit")
        mock_commit.side_effect = SQLAlchemyError("Fallo de conexión simulado")

        mock_rollback = mocker.patch("app.api.autores.services.db.session.rollback")
        
        response, status = actualizar_autor_service(1,test_data)

        mock_commit.assert_called_once()
        mock_rollback.assert_called_once()

        assert status == 500
        assert "error" in response


def test_eliminar_autor_service_error_db(app,mocker):
    with app.app_context():
        mock_autor_existente = MagicMock()
        mock_autor_existente.id_autor = 1
        mock_autor_existente.nombre_completo = "Daniel Cabello"
        mock_autor_existente.nacionalidad = "Chileno"
        mock_autor_existente.slug_autor = "daniel-cabello-1"

        mock_autor_existente.to_dict.return_value = {
            "id_autor": 1,
            "nombre_completo": "Danielo Cabellera",
            "nacionalidad": "Peruano",
            "slug_autor": "danielo-cabellera-1" 
        }


        mock_autores = mocker.patch("app.api.autores.services.Autores")
        mock_autores.query.get.return_value = mock_autor_existente



        mock_delete = mocker.patch("app.api.autores.services.db.session.delete")
        mock_delete.side_effect = SQLAlchemyError("Fallo de conexión simulado en eliminar")

        mock_rollback = mocker.patch("app.api.autores.services.db.session.rollback")
        
        response, status = eliminar_autor_service(1)

        mock_delete.assert_called_once()
        mock_rollback.assert_called_once()

        assert status == 500
        assert "error" in response
        assert response["error"] == "Error al eliminar autor: Fallo de conexión simulado en eliminar"

def test_eliminar_autor_service_exitoso(app,mocker):
    with app.app_context():
        mock_autor_existente = MagicMock()
        mock_autor_existente.id_autor = 1
        mock_autor_existente.nombre_completo = "Daniel Cabello"
        mock_autor_existente.nacionalidad = "Chileno"
        mock_autor_existente.slug_autor = "daniel-cabello-1"

        mock_autor_existente.to_dict.return_value = {
            "id_autor": 1,
            "nombre_completo": "Danielo Cabellera",
            "nacionalidad": "Peruano",
            "slug_autor": "danielo-cabellera-1" 
        }


        mock_autores = mocker.patch("app.api.autores.services.Autores")
        mock_autores.query.get.return_value = mock_autor_existente



        mock_delete = mocker.patch("app.api.autores.services.db.session.delete")
        mock_commit = mocker.patch("app.api.autores.services.db.session.commit")

        
        response, status = eliminar_autor_service(1)

        mock_delete.assert_called_once()
        mock_commit.assert_called_once()

        assert status == 200
        assert response["mensaje"] == "Autor eliminado correctamente"
        assert response["autor"] == {
            "id_autor" : 1,
            "nombre_completo" : "Danielo Cabellera",
            "nacionalidad" : "Peruano",
            "slug_autor" : "danielo-cabellera-1"
        }

def test_eliminar_autor_service_autor_no_encontrado(app,mocker):
    with app.app_context():
        mock_autores = mocker.patch("app.api.autores.services.Autores")
        mock_autores.query.get.return_value = None

        response, status = eliminar_autor_service(1)

        assert status == 404
        assert response["error"] == "Autor no encontrado"