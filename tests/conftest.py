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
    """
    Un usuario simulado y más detallado para pruebas, compatible con la fixture login_as.
    """
    def __init__(self, id="1", rol="usuario", is_authenticated=True):
        self.id = id  # Atributo 'id' requerido por la fixture 'login_as'
        self.id_usuario = id #Viene de nuestro modelo
        self.rol = rol
        self._is_authenticated = is_authenticated
        
        # Atributos adicionales para tests más detallados
        self.correo_institucional = "tomas.hernandez@umce.cl"
        self.nombre_usuario = "Tomás Hernández"
        self.foto_perfil = "foto_perfil_test.png"

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    def get_id(self):
        """Devuelve el ID del usuario como string, requerido por Flask-Login."""
        return str(self.id)


@pytest.fixture
def login_as(client):
    """
    Fixture para loguear a un usuario simulado.
    Registra un user_loader temporal para el test y lo restaura después.
    """
    user_store = {}

    # 1. Guarda el user_loader original para poder restaurarlo después.
    original_loader = login_manager.user_loader

    # 2. Define y registra nuestro user_loader simulado.
    def _mock_user_loader(user_id):
        return user_store.get(user_id)
    login_manager.user_loader(_mock_user_loader)

    # 3. La función que los tests usarán para "iniciar sesión".
    def _login(rol):
        user = MockUser(rol=rol)
        user_store[user.id] = user
        with client.session_transaction() as session:
            session['_user_id'] = user.id
            session['_fresh'] = True
    
    # 4. Entrega el control al test.
    yield _login

    # 5. Limpieza: restaura el user_loader original.
    login_manager._user_loader = original_loader
    with client.session_transaction() as session:
        session.clear()


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
