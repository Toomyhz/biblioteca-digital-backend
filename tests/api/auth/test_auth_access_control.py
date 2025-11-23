def test_admin_access_granted(client, login_as):
    """
    Prueba que un usuario con el rol 'admin' puede acceder a una ruta
    protegida que requiere dicho rol.
    """
    login_as("admin")
    response = client.get("/admin-only")
    
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "Acceso de Admin concedido"


def test_admin_access_forbidden_for_user_role(client, login_as):
    """
    Prueba que un usuario con el rol 'usuario' no puede acceder a una
    ruta que requiere el rol 'admin'.
    """
    login_as("usuario")
    response = client.get("/admin-only")
    
    assert response.status_code == 403
    data = response.get_json()
    assert data["message"] == "Forbidden"
    assert data["required"] == ["admin"]


def test_user_access_granted(client, login_as):
    """
    Prueba que un usuario con el rol 'usuario' puede acceder a una ruta
    que requiere ese rol.
    """
    login_as("usuario")
    response = client.get("/usuario")
    
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "Acceso de usuario"


def test_user_access_forbidden_for_admin_role(client, login_as):
    """
    Prueba que un usuario con el rol 'admin' no puede acceder a una
    ruta que requiere el rol 'usuario'.
    """
    login_as("admin")
    response = client.get("/usuario")

    assert response.status_code == 403
    data = response.get_json()
    assert data["message"] == "Forbidden"
    assert data["required"] == ["usuario"]


def test_access_forbidden_for_anonymous_user(client):
    """
    Prueba que un usuario no autenticado no puede acceder a ninguna
    ruta protegida.

    Dependiendo de tu configuración de Flask-Login:
    - si NO tienes login_view -> 401
    - si tienes login_view configurado -> 302 redirect al login
    """
    response_admin = client.get("/admin-only")
    assert response_admin.status_code in (401, 302)

    response_user = client.get("/usuario")
    assert response_user.status_code in (401, 302)
