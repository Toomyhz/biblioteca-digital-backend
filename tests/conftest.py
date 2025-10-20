# tests/conftest.py
import pytest
from flask_login import login_user, logout_user
from unittest.mock import patch

from app import create_app, db
from app.extensions import login_manager

import fakeredis

@pytest.fixture(scope="module")
def app():
    """Crea una instancia de la aplicación para toda la sesión de pruebas."""
    app = create_app("app.config.TestingConfig", testing=True)
    
    # Rutas de prueba
    with app.app_context():
        # Decorador para testeo
        from app.api.auth.access_control import roles_required

        @app.route("/admin-only")
        @roles_required("admin")
        def admin_view():
            return "Acceso de Admin concedido", 200

        @app.route("/usuario")
        @roles_required("usuario")
        def usuario_view():
            return "Acceso de usuario", 200
    yield app 

@pytest.fixture(scope="function")
def test_db(app):
    """Crea y limpia la DB por cada test"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app, test_db):
    """Cliente HTTP de test"""
    return app.test_client()

class MockUser:
    """Usuario simulado para pruebas"""
    def __init__(self,rol="usuario",is_authenticated=True):
        self._is_authenticated = is_authenticated
        self.id_usuario = "1"
        self.correo_institucional = "tomas.hernandez@umce.cl"
        self.nombre_usuario = "Tomás Hernández"
        self.foto_perfil = "foto_perfil.png"
        self.rol = rol
    
    @property
    def is_authenticated(self):
        return self._is_authenticated

    # Métodos requeridos por Flask-Login
    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    def get_id(self):
        return "1"

@pytest.fixture
def login_as(app,client):
    """
    Fixture para loguear a un usuario simulado con un rol específico.
    """
    user_store = {}

    def _login(rol):
        user = MockUser(rol=rol)
        user_store["1"] = user
        
        with app.test_request_context():
            login_user(user)
    
    with patch.object(login_manager,'user_loader') as mock_user_loader:
        mock_user_loader.side_effect = lambda user_id: user_store.get(user_id)
        yield _login

    with app.test_request_context():
        logout_user()

@pytest.fixture(scope="function",autouse=True)
def mock_redis(monkeypatch):
    """
    Monkeypatch para reemplazar la instancia de Redis ANTES de que los tests se recolecten. Evita error de importación
    "autouse" significa que se aplicará automaticamente sin pedirlo.
    """
    # Se crea el cliente falso de Redis
    fake_redis_client = fakeredis.FakeRedis()
    monkeypatch.setattr(
        "app.api.auth.services.get_redis",
        lambda: fake_redis_client
    )
