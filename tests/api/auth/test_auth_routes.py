from unittest.mock import patch
from flask import redirect

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
            "foto_perfil":"foto_perfil_test.png",
            "rol":"usuario"
        }
    }

def test_usuario_actual_no_logueado(client):
    response = client.get("/api/auth/me/")
    json_data = response.get_json()
    assert response.status_code == 401
    assert json_data == {
        "is_authenticated":False,
        "user":None
    }

def test_usuario_actual_admin(client, login_as):
    login_as("admin")
    response = client.get("/api/auth/me/admin/")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data == {
        "is_authenticated":True,
        "is_admin":True
    }

def test_cierre_sesion_exitoso(client, login_as):
    login_as("usuario")
    response = client.post("/api/auth/logout/")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data == {
        "message":"Sesión cerrada correctamente"
    }
    response_despues = client.get("/api/auth/me/")
    json_posterior = response_despues.get_json()
    assert response_despues.status_code == 401
    assert json_posterior == {
        "is_authenticated":False,
        "user":None
    }

def test_cierre_sesion_sin_user_logeado(client):
    response = client.post("/api/auth/logout/")
    json_data = response.get_json()
    assert response.status_code == 401
    assert json_data == {
        "message":"No hay sesión activa para cerrar"
    }

def test_login_redirige_correctamente(client):
    url_esperada = "https://accounts.google.com/o/oauth2/v2/auth?params=mocked"

    with patch("app.api.auth.routes._build_google_auth_url", return_value = url_esperada) as mock_build_url:

        response = client.get("/api/auth/login/")

        mock_build_url.assert_called_once()

        assert response.status_code == 302

        assert response.location == url_esperada

def test_callback_error(client):
    error_code_from_google = "access_denied"
    callback_url_with_error = f"/api/auth/callback/?error={error_code_from_google}"
    expected_frontend_redirect_url = f"http://localhost:5173/login?auth_error={error_code_from_google}"
    response = client.get(callback_url_with_error)
    assert response.status_code == 302
    assert response.location == expected_frontend_redirect_url

def test_callback_exitoso(client):

    state = "un-estado-valido"
    code = "un-codigo-de-autorizacion"
    callback_url_success = f"/api/auth/callback/?state={state}&code={code}"

    expected_redirect_url = "http://localhost:5173/auth/success"
    expected_response = redirect(expected_redirect_url)

    with patch("app.api.auth.routes.manejar_callback",return_value=expected_response) as mock_handler:
        response = client.get(callback_url_success)

        mock_handler.assert_called_once()
        assert response.status_code == 302
        assert response.location == expected_redirect_url