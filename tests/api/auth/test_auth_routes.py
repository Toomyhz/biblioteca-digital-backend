def test_usuario_actual_logueado(client, login_as):
    login_as("usuario")
    response = client.get("/api/auth/me/")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data == {
        "is_authenticated":True,
        "user":{
            "id":"1",
            "correo_institucional":"tomas.hernandez@umce.cl",
            "nombre_usuario":"Tomás Hernández",
            "foto_perfil":"foto_perfil.png",
            "rol":"usuario"
        }
    }
