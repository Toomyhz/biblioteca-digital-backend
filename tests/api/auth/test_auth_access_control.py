import json

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
    data = json.loads(response.data)
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
    data = json.loads(response.data)
    assert data["message"] == "Forbidden"
    assert data["required"] == ["usuario"]

def test_access_forbidden_for_anonymous_user(client):
    """
    Prueba que un usuario no autenticado no puede acceder a ninguna
    ruta protegida. 
    Flask-Login usualmente retorna 401 Unauthorized para usuarios no logueados
    en lugar del 403 del decorador, lo cual es el comportamiento esperado.
    """
    response_admin = client.get("/admin-only")
    assert response_admin.status_code == 401 # O podría ser una redirección 302 si tienes un login_view configurado

    response_user = client.get("/usuario")
    assert response_user.status_code == 401
