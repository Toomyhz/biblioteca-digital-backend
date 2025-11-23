import pytest
from unittest.mock import MagicMock

def test_listar_autores_endpoint(client, mocker):
    # 1. ARRANGE
    datos_falsos = [
        {"id": 1, "nombre_completo": "Autor 1", "nacionalidad": "Chilena"},
        {"id": 2, "nombre_completo": "Autor 2", "nacionalidad": "Argentina"}
    ]
    
    mock_servicio = mocker.patch("app.api.autores.controllers.listar_autores_service", return_value=datos_falsos)

    # 2. ACT
    response = client.get("/api/autores/")
    json_data = response.get_json()

    # 3. ASSERT
    assert response.status_code == 200
    assert len(json_data["data"]) == 2
    assert json_data["data"][0]["nombre_completo"] == "Autor 1"
    mock_servicio.assert_called_once()


def test_agregar_autor_endpoint(client, mocker):
    # 1. ARRANGE
    # Asegúrate que estos campos coincidan con tu modelo RestX ('input')
    data_entrada = {
        "nombre_completo": "Danielo Cabellera", 
        "nacionalidad": "Peruano",
        "slug_autor": "danielo-cabellera"
    }
    mock_autor_respuesta = MagicMock()
    mock_autor_respuesta.id_autor = 1
    mock_autor_respuesta.nombre_completo = "Danielo Cabellera"
    mock_autor_respuesta.nacionalidad = "Peruano"
    mock_autor_respuesta.slug_autor = "danielo-cabellera"


    mock_servicio = mocker.patch("app.api.autores.controllers.agregar_autor_service", return_value=mock_autor_respuesta)
    mock_db_commit = mocker.patch("app.api.autores.controllers.db.session.commit")
    # 2. ACT
    response = client.post("/api/autores/", json=data_entrada)
    json_data = response.get_json()

    # 3. ASSERT
    assert response.status_code == 201
    assert json_data["autor"]["nombre_completo"] == "Danielo Cabellera"
    # Verificamos que al servicio le llegó la data correcta
    mock_servicio.assert_called_once_with(data_entrada)

    mock_db_commit.assert_called_once()

def test_actualizar_autor_endpoint(client, mocker):
    # 1. ARRANGE
    data_update = {"nombre_completo": "Marco Antonio Solis", "nacionalidad": "Mexicano"}
    mock_autor_respuesta = MagicMock()
    mock_autor_respuesta.id_autor = 1
    mock_autor_respuesta.nombre_completo = "Marco Antonio Solis"
    mock_autor_respuesta.nacionalidad = "Mexicano"
    mock_autor_respuesta.slug_autor = "marco-antonio-solis"

    
    mock_servicio = mocker.patch("app.api.autores.controllers.actualizar_autor_service", return_value=mock_autor_respuesta)
    
    # 2. ACT
    # Nota: Flask pasa los parámetros de URL como strings
    response = client.put("/api/autores/1", json=data_update)
    json_data = response.get_json()

    # 3. ASSERT
    assert response.status_code == 200
    assert json_data["mensaje"] == "Autor actualizado correctamente"
    
    # Verificamos argumentos: ID "1" y la data
    mock_servicio.assert_called_once_with("1", data_update)


def test_eliminar_autor_endpoint(client, mocker):
    # 1. ARRANGE
    respuesta_servicio = ({"mensaje": "Autor eliminado correctamente"}, 200)
    
    mock_servicio = mocker.patch("app.api.autores.controllers.eliminar_autor_service", return_value=respuesta_servicio)
    
    # 2. ACT
    response = client.delete("/api/autores/1")
    
    # 3. ASSERT
    assert response.status_code == 200
    assert response.get_json()["mensaje"] == "Autor eliminado correctamente"
    mock_servicio.assert_called_once_with("1")