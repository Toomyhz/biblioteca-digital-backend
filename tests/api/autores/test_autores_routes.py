def test_agregar_autor_endpoint(client,mocker):
    data = {"new_nombre":"Autor Prueba", "new_nacionalidad":"Chilena"}
    mock_respuesta_servicio = {
        "mensaje":"autor agregado correctamente",
        "autor": {
            "id_autor" : 1,
            "nombre_completo" : "Danielo Cabellera",
            "nacionalidad" : "Peruano",
            "slug_autor" : "danielo-cabellera-1"
        }
    },201

    mock_agregar_servicio =mocker.patch("app.api.autores.controllers.agregar_autor_service",return_value = mock_respuesta_servicio)

    response = client.post("/api/autores/", json=data)

    json_data = response.get_json()
    assert response.status_code == 201
    assert json_data["autor"]["nombre_completo"] == "Danielo Cabellera"
    mock_agregar_servicio.assert_called_once_with(data)

def test_listar_autores_endpoint(client):
    response = client.get("/api/autores/")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data == []



def test_actualizar_autor_endpoint(client,mocker):
    data = {"edit_nacionalidad":"Americano","edit_nombre":"Marco Antonio Solis"}
    mock_respuesta_servicio = {
        "mensaje":"autor agregado correctamente",
        "autor": {
            "id_autor" : 1,
            "nombre_completo" : "Marco Antonio Solis",
            "nacionalidad" : "Americano",
            "slug_autor" : "marco-antonio-solis-1"
        }
    },201
    mock_actualizar_servicio =mocker.patch("app.api.autores.controllers.actualizar_autor_service",return_value = mock_respuesta_servicio)
    response = client.put("/api/autores/1",json=data)
    json_data = response.get_json()
    assert response.status_code == 201
    assert json_data["mensaje"] == "autor agregado correctamente"
    print(f"ARGUMENTOS RECIBIDOS POR EL MOCK: {mock_actualizar_servicio.call_args}")
    mock_actualizar_servicio.assert_called_once_with("1", data)



def test_eliminar_autor_endpoint(client,mocker):
    mock_respuesta_servicio = {
        "mensaje":"Autor eliminado correctamente",
        "autor": {
            "id_autor" : 1,
            "nombre_completo" : "Marco Antonio Solis",
            "nacionalidad" : "Americano",
            "slug_autor" : "marco-antonio-solis-1"
        }
    },200
    mock_eliminar_servicio =mocker.patch("app.api.autores.controllers.eliminar_autor_service",return_value = mock_respuesta_servicio)
    response = client.delete("/api/autores/1")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["mensaje"] == "Autor eliminado correctamente"
    mock_eliminar_servicio.assert_called_once_with("1")