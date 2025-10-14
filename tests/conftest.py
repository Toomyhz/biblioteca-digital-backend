# tests/conftest.py
import pytest
from app import create_app, db

@pytest.fixture(scope="module")
def test_app():
    """Crea la app Flask para testing"""
    app = create_app("app.config.TestingConfig", testing=True)
    with app.app_context():
        yield app  # aquí ya estamos dentro del contexto

@pytest.fixture(scope="function")
def test_db(test_app):
    """Crea y limpia la DB por cada test"""
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope="function")
def client(test_app, test_db):
    """Cliente HTTP de test"""
    with test_app.test_client() as client:
        yield client

class MockUser:
    """Usuario de prueba"""
    def __init__(self,role="usuario",is_authenticated=True):
        self.role = role
        self.is_authenticated = is_authenticated
        self.is_active = True
        self.is_anonymous = not is_authenticated

    def get_id(self):
        return "1"