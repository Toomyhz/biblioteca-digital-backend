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
    response = client.delete("/api/biblioteca/")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["mensaje"] == "Autor eliminado correctamente"
    mock_eliminar_servicio.assert_called_once_with("1")