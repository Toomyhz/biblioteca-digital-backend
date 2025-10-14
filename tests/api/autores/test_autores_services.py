import pytest

def test_listar_autores_endpoint(client):
    response = client.get("/api/autores/")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data == []

def test_agregar_autor_endpoint(client):
    data = {"new_nombre":"Autor Prueba", "new_nacionalidad":"Chilena"}
    response = client.post("/api/autores/", json=data)
    json_data = response.get_json()
    assert response.status_code == 201
    assert json_data["autor"]["nombre_completo"] == "Autor Prueba"

def test_actualizar_autor_endpoint(client):
    data = {"edit_nombre":"Marco Antonio Solis","edit_nacionalidad":"Americano"}
    response = client.put("/api/autores/1",json=data)
    json_data = response.get_json()
    assert response.status_code == 404
    assert "error" in json_data
    
def test_actualizar_autor_endpoint_no_encontrado(client):
    data = {"edit_nombre":"Marco Antonio Solis","edit_nacionalidad":"Americano"}
    response = client.put("/api/autores/98",json=data)
    json_data = response.get_json()
    assert response.status_code == 404
    assert "error" in json_data
    assert json_data["error"]["error"] == "Autor no encontrado"

def test_borrar_autor_endpoint_no_encontrado(client):
    response = client.delete("/api/autores/98")
    json_data = response.get_json()
    assert response.status_code == 404
    assert "error" in json_data
    assert json_data["error"]["error"] == "Autor no encontrado"