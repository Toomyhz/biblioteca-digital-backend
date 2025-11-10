# tests/conftest.py
import pytest
from flask_login import login_user, logout_user
from unittest.mock import patch

from app import create_app, db
from app.extensions import login_manager

import fakeredis
import os
from werkzeug.datastructures import FileStorage
from io import BytesIO
from app import create_app, db
from app.models.autores import Autores
from app.models.carreras import Carreras
from app.models.libros import Libros


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

# Fixtures para autores


@pytest.fixture
def autor_fixture(test_db):
    """Crear un autor de prueba"""
    autor = Autores(
        nombre_completo="Alexandre Dumas",
        nacionalidad="Francia",
        slug_autor="alexandre-dumas"
    )
    test_db.session.add(autor)
    test_db.session.commit()
    test_db.session.refresh(autor)
    return autor


@pytest.fixture
def autores_multiples(test_db):
    """Crea múltiples autores"""
    autores = [
        Autores(nombre_completo="Isabel Allende",
                nacionalidad="Chilena", slug_autor="isabel-allende"),
        Autores(nombre_completo="Jorge Luis Borges",
                nacionalidad="Argentina", slug_autor="jorge-luis-borges"),
        Autores(nombre_completo="Pablo Neruda",
                nacionalidad="Chilena", slug_autor="pablo-neruda"),
    ]
    test_db.session.add_all(autores)
    test_db.session.commit()

    # Recargar para obtener IDs
    for autor in autores:
        test_db.session.refresh(autor)

    return autores

# Fixtures para carreras


@pytest.fixture
def carrera_fixture(test_db):
    """Crea una carrera de prueba"""
    carrera = Carreras(
        nombre_carrera="Ingeniería en Computación",
        slug_carrera="ingenieria-en-computacion"
    )
    test_db.session.add(carrera)
    test_db.session.commit()
    test_db.session.refresh(carrera)
    return carrera


@pytest.fixture
def carreras_multiples(test_db):
    """Crea múltiples carreras de prueba"""
    carreras = [
        Carreras(
            nombre_carrera="Pedagogía en Ciencias",
            slug_carrera="pedagogia-en-ciencias"
        ),
        Carreras(
            nombre_carrera="Pedagogía en Matemáticas",
            slug_carrera="pedagogia-en-matematicas"
        ),
        Carreras(
            nombre_carrera="Pedagogía en Lenguas",
            slug_carrera="pedagogia-en-leguans"
        )
    ]
    test_db.session.add_all(carreras)
    test_db.session.commit()

    for carrera in carreras:
        test_db.session.refresh(carrera)

    return carrera
# Fixtures para libros C:


@pytest.fixture
def libro_fixture(test_db, autor_fixture, carrera_fixture):
    libro = Libros(
        titulo="Los Tres Mosqueteros",
        isbn="978-1234567890",
        anio_publicacion="1844",
        estado="disponible",
        archivo_pdf="tres-mosqueteros.pdf",
        slug_titulo="tres-mosqueteros"
    )
    test_db.session.add(libro)
    test_db.session.flush()

    libro.autores.append(autor_fixture)
    libro.carreras.append(carrera_fixture)

    test_db.session.commit()
    test_db.session.refresh(libro)
    return libro


@pytest.fixture
def libros_multiples(test_db, autores_multiples, carreras_multiples):
    """Crea múltiples libros para pruebas de listado/búsqueda"""
    libros = [
        Libros(
            titulo="La Casa de los Espíritus",
            isbn="978-1-11-111111-1",
            anio_publicacion=1982,
            estado="disponible",
            archivo_pdf="casa-espiritus.pdf",
            slug_titulo="la-casa-de-los-espiritus"
        ),
        Libros(
            titulo="El Aleph",
            isbn="978-2-22-222222-2",
            anio_publicacion=1949,
            estado="prestado",
            archivo_pdf="el-aleph.pdf",
            slug_titulo="el-aleph"
        ),
        Libros(
            titulo="Veinte Poemas de Amor",
            isbn="978-3-33-333333-3",
            anio_publicacion=1924,
            estado="disponible",
            archivo_pdf="veinte-poemas.pdf",
            slug_titulo="veinte-poemas-de-amor"
        )
    ]

    # Asignar autores y carreras
    libros[0].autores.append(autores_multiples[0])
    libros[0].carreras.append(carreras_multiples[0])

    libros[1].autores.append(autores_multiples[1])
    libros[1].carreras.append(carreras_multiples[1])

    libros[2].autores.append(autores_multiples[2])
    libros[2].carreras.append(carreras_multiples[2])

    test_db.session.add_all(libros)
    test_db.session.commit()

    for libro in libros:
        test_db.session.refresh(libro)

    return libros

# Fixtures para los archivos PDF


@pytest.fixture
def mock_pdf():
    """Crea un archivo PDF falso para testing"""
    pdf_content = b"%PDF-1.4\n%PDF falso para motivos de testing"
    return FileStorage(
        stream=BytesIO(pdf_content),
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


@pytest.fixture
def temp_pdf_folder(tmp_path):
    """Crea una carpeta temporal para PDFs de prueba"""
    pdf_folder = tmp_path / "test_pdfs"
    pdf_folder.mkdir()
    return str(pdf_folder)

# Fixtures de limpieza


@pytest.fixture(autouse=True)
def cleanup_files(test_app):
    """Limpia archivos temporales después de cada test"""
    yield

    # Limpiar carpeta de PDFs de test si existe
    import shutil
    pdf_folder = test_app.config.get('PDF_UPLOAD_FOLDER')
    if pdf_folder and os.path.exists(pdf_folder) and 'test' in pdf_folder.lower():
        try:
            shutil.rmtree(pdf_folder)
        except:
            pass

# Helper para debbug


@pytest.fixture
def print_db_state(test_db):
    """Helper para debuggear estado de la BD"""
    def _print():
        print("\n" + "="*60)
        print("ESTADO DE LA BASE DE DATOS")
        print("="*60)

        autores_count = test_db.session.query(Autores).count()
        carreras_count = test_db.session.query(Carreras).count()
        libros_count = test_db.session.query(Libros).count()

        print(f"Autores: {autores_count}")
        print(f"Carreras: {carreras_count}")
        print(f"Libros: {libros_count}")
        print("="*60 + "\n")

    return _print


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
