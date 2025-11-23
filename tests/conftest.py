# tests/conftest.py
import pytest
from unittest.mock import MagicMock
from flask import Flask
import fakeredis
from werkzeug.datastructures import FileStorage
from io import BytesIO


from app import create_app
from app.models.usuarios import login_manager
from app.models.autores import Autores
from app.models.carreras import Carreras
from app.models.libros import Libros

from flask_login import UserMixin
from dataclasses import dataclass

from app.api.auth.access_control import roles_required


@pytest.fixture(scope="module")
def app():
    app = create_app("app.config.TestingConfig", testing=True)

    # Ajustes extra de test (por si acaso):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    # 1) MOCKEAR user_loader GLOBALMENTE EN TEST
    #    Esto hace que Flask-Login NUNCA use db ni el modelo Usuarios en los tests.
    def test_user_loader(user_id: str):
        # Acepta ids tipo "1_admin", "1_usuario", etc.
        parts = user_id.split("_")
        rol = parts[1] if len(parts) == 2 else "usuario"
        return MockUser(id=user_id, rol=rol)

    login_manager.user_loader(test_user_loader)

    # 2) Rutas de prueba protegidas con el decorador
    @app.route("/admin-only")
    @roles_required("admin")
    def admin_view():
        return "Acceso de Admin concedido", 200

    @app.route("/usuario")
    @roles_required("usuario")
    def usuario_view():
        return "Acceso de usuario", 200

    return app


@pytest.fixture
def client(app):
    # Nuevo client (y nueva sesión) en cada test
    with app.test_client() as client:
        yield client

@pytest.fixture()
def autor_mock():
    """Crear un autor de prueba"""
    autor = Autores(
        nombre_completo="Alexandre Dumas",
        nacionalidad="Francia",
        slug_autor="alexandre-dumas"
    )
    autor.id = 1
    return autor

@pytest.fixture
def carrera_mock():
    """Crea una carrera de prueba"""
    carrera = Carreras(
        nombre_carrera="Ingeniería en Computación",
        slug_carrera="ingenieria-en-computacion"
    )
    carrera.id = 10
    return carrera

    
@pytest.fixture
def libro_mock(autor_mock, carrera_mock):
    libro = Libros(
        titulo="Los Tres Mosqueteros",
        isbn="978-1234567890",
        anio_publicacion="1844",
        estado="disponible",
        archivo_pdf="tres-mosqueteros.pdf",
        slug_titulo="tres-mosqueteros"
    )
    libro.id = 22

    libro.autores = [autor_mock]
    libro.carreras = [carrera_mock]
    return libro


@pytest.fixture
def mock_pdf():
    return FileStorage(
        stream=BytesIO(b"%PDF-1.4\nContenido falso"),
        filename="test_libro.pdf",
        content_type="application/pdf"
    )


@pytest.fixture
def mock_txt():
    """Crea un archivo TXT falso para probar validación de tipo"""
    txt_content = b"Esto no es un PDF"
    return FileStorage(
        stream=BytesIO(txt_content),
        filename="test_libro.txt",
        content_type="text/plain",
    )


@dataclass
class MockUser(UserMixin):
    id: str = "1"
    id_usuario: str = "1"
    rol: str = "usuario"
    correo_institucional: str = "test@umce.cl"
    foto_perfil: str = "foto_perfil_test.png"
    nombre_usuario: str = "Test_Nombre Test_Apellido"

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


@pytest.fixture
def login_as(client):
    """
    Simula login escribiendo directamente en la sesión.
    El user_loader de test interpretará el ID para construir el MockUser.
    """
    def _login(rol: str):
        fake_id = f"1_{rol}"  # "1_admin", "1_usuario", etc.
        with client.session_transaction() as sess:
            sess["_user_id"] = fake_id
            sess["_fresh"] = True

    return _login

@pytest.fixture(autouse=True)
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
