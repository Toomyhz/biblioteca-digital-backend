import pytest
from app.api.autores.controllers import agregar_autor, actualizar_autor, eliminar_autor
from sqlalchemy.exc import IntegrityError, DataError
from app.api.exceptions import RegistroExistenteError, NotFoundError

def test_agregar_autor_controller_integrity_error(mocker):
    # Mock rollback
    mock_db_rollback = mocker.patch(
        "app.api.autores.controllers.db.session.rollback"
    )

    # Mock servicio que lanza IntegrityError
    mock_servicio = mocker.patch(
        "app.api.autores.controllers.agregar_autor_service"
    )
    mock_servicio.side_effect = IntegrityError(
        statement=None, params=None, orig=None
    )

    data_entrada = {
        "nombre_completo": "Juan Perez",
        "nacionalidad": "Chilena",
        "slug_autor": "juan-perez"
    }

    # Verificamos que la excepción se lanza
    with pytest.raises(RegistroExistenteError) as exc_info:
        agregar_autor(data_entrada)

    # Mensaje correcto
    assert str(exc_info.value) == "Ya existe un autor con ese slug o nombre."

    # Confirmar que se llamó rollback()
    mock_db_rollback.assert_called_once()

    # Confirmar que se llamó el servicio
    mock_servicio.assert_called_once_with(data_entrada)

def test_agregar_autor_controller_registro_existente_error(mocker):
    # Mock rollback
    mock_db_rollback = mocker.patch(
        "app.api.autores.controllers.db.session.rollback"
    )

    mock_servicio = mocker.patch(
        "app.api.autores.controllers.agregar_autor_service"
    )
    mock_servicio.side_effect = RegistroExistenteError(
        "Ya existe un autor con ese slug o nombre."
    )

    data_entrada = {
        "nombre_completo": "Juan Perez",
        "nacionalidad": "Chilena",
        "slug_autor": "juan-perez"
    }

    # Verificamos que la excepción se lanza
    with pytest.raises(RegistroExistenteError) as exc_info:
        agregar_autor(data_entrada)

    # Mensaje correcto
    assert str(exc_info.value) == "Ya existe un autor con ese slug o nombre."

    # Confirmar que se llamó rollback()
    mock_db_rollback.assert_called_once()

    # Confirmar que se llamó el servicio
    mock_servicio.assert_called_once_with(data_entrada)


def test_actualizar_autor_controller_integrity_error(mocker):
    # Mock rollback
    mock_db_rollback = mocker.patch(
        "app.api.autores.controllers.db.session.rollback"
    )

    # Mock servicio que lanza IntegrityError
    mock_servicio = mocker.patch(
        "app.api.autores.controllers.actualizar_autor_service"
    )
    mock_servicio.side_effect = IntegrityError(
        statement=None, params=None, orig=None
    )

    data_entrada = {
        "nombre_completo": "Juan Perez",
        "nacionalidad": "Chilena",
        "slug_autor": "juan-perez"
    }

    # Verificamos que la excepción se lanza
    with pytest.raises(RegistroExistenteError) as exc_info:
        actualizar_autor("1",data_entrada)

    # Mensaje correcto
    assert str(exc_info.value) == "El autor actualizado entra en conflicto con otro existente."

    # Confirmar que se llamó rollback()
    mock_db_rollback.assert_called_once()

    # Confirmar que se llamó el servicio
    mock_servicio.assert_called_once_with("1", data_entrada)

def test_actualizar_autor_controller_not_found_error(mocker):
    # Mock rollback
    mock_db_rollback = mocker.patch(
        "app.api.autores.controllers.db.session.rollback"
    )

    mock_servicio = mocker.patch(
        "app.api.autores.controllers.actualizar_autor_service"
    )
    mock_servicio.side_effect = NotFoundError(
    )

    data_entrada = {
        "nombre_completo": "Juan Perez",
        "nacionalidad": "Chilena",
        "slug_autor": "juan-perez"
    }

    # Verificamos que la excepción se lanza
    with pytest.raises(NotFoundError):
        actualizar_autor("1",data_entrada)


    # Confirmar que se llamó rollback()
    mock_db_rollback.assert_called_once()

    # Confirmar que se llamó el servicio
    mock_servicio.assert_called_once_with("1",data_entrada)


def test_eliminar_autor_controller_not_found_error(mocker):
    # Mock rollback
    mock_db_rollback = mocker.patch(
        "app.api.autores.controllers.db.session.rollback"
    )

    mock_servicio = mocker.patch(
        "app.api.autores.controllers.eliminar_autor_service"
    )
    mock_servicio.side_effect = NotFoundError(
    )
    # Verificamos que la excepción se lanza
    with pytest.raises(NotFoundError):
        eliminar_autor("1")

    # Confirmar que se llamó rollback()
    mock_db_rollback.assert_called_once()

    # Confirmar que se llamó el servicio
    mock_servicio.assert_called_once_with("1")