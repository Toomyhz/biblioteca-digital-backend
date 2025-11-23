import pytest
from unittest.mock import patch, MagicMock, mock_open
from werkzeug.datastructures import ImmutableMultiDict
from app.api.libros.services import archivos_permitidos, agregar_libro_service, listar_libros_service, eliminar_libro_service
from app.api.exceptions import NotFoundError, ServiceError
from app.models.libros import Libros


class TestArchivosPermitidos:

    def test_acepta_pdf_minusculas(self):
        """Acepta archivos .pdf en minúsculas"""
        assert archivos_permitidos("documento.pdf") == True

    def test_acepta_pdf_mayusculas(self):
        """Acepta archivos .PDF en mayúsculas"""
        assert archivos_permitidos("DOCUMENTO.PDF") == True

    def test_acepta_pdf_mixto(self):
        """Acepta archivos .PdF en mixto"""
        assert archivos_permitidos("documento.PdF") == True

    def test_rechaza_txt(self):
        """Rechaza archivos .txt"""
        assert archivos_permitidos("documento.txt") == False

    def test_rechaza_jpg(self):
        """Rechaza archivos .jpg"""
        assert archivos_permitidos("imagen.jpg") == False

    def test_rechaza_exe(self):
        """Rechaza archivos .exe"""
        assert archivos_permitidos("virus.exe") == False
        assert archivos_permitidos("virus.exe") == False

    def test_rechaza_sin_extension(self):
        """Rechaza archivos sin extensión"""
        assert archivos_permitidos("documento") == False

    def test_rechaza_vacio(self):
        """Rechaza string vacío"""
        assert archivos_permitidos("") == False

    def test_multiples_puntos(self):
        """Maneja archivos con múltiples puntos"""
        assert archivos_permitidos("mi.libro.final.pdf") == True
        assert archivos_permitidos("mi.libro.final.txt") == False

class TestListarLibrosService():
    def test_listar_libros_vacio(self,mocker):
        fake_paginacion = mocker.Mock(
            items=[],
            page=1,
            per_page=10,
            total=0,
            pages=0,
        )

        fake_query = mocker.Mock()
        fake_query.order_by.return_value.paginate.return_value = fake_paginacion

        mocker.patch(
            "app.api.libros.services.db.session.query",
            return_value=fake_query,
        )

        result = listar_libros_service(1, 10, None)

        assert result["data"] == []
        assert result["paginacion"]["total"] == 0


    def test_listar_libros_con_resultados(self,mocker):
        # Libros simulados
        libro = mocker.Mock()
        libro.to_dict.return_value = {"id_libro": 1}

        fake_paginacion = mocker.Mock(
            items=[libro],
            page=1,
            per_page=10,
            total=1,
            pages=1,
        )

        fake_query = mocker.Mock()
        fake_query.order_by.return_value.paginate.return_value = fake_paginacion

        mocker.patch(
            "app.api.libros.services.db.session.query",
            return_value=fake_query,
        )

        result = listar_libros_service(1, 10, None)

        assert result["data"] == [{"id_libro": 1}]
        assert result["paginacion"]["total"] == 1

   
def test_listar_libros_con_busqueda_aplica_filtro(mocker):

    fake_paginacion = mocker.Mock(
        items=[],
        page=1,
        per_page=10,
        total=0,
        pages=0,
    )

    fake_filtered = mocker.Mock()
    fake_filtered.order_by.return_value.paginate.return_value = fake_paginacion

    fake_query = mocker.Mock()
    fake_query.filter.return_value = fake_filtered

    mocker.patch(
        "app.api.libros.services.db.session.query",
        return_value=fake_query,
    )

    listar_libros_service(1, 10, "Hola")

    fake_query.filter.assert_called_once()

   
class TestAgregarLibroService:
    """Tests para agregar_libro_service"""

    def test_sin_titulo_retorna_error(self, test_app):
        """Rechaza libro sin título"""

        with test_app.app_context():
            data = ImmutableMultiDict([("new_isbn", "123456")])
            archivo = {}

            response, status = agregar_libro_service(data, archivo)

            assert status == 400
            assert "error" in response
            assert "título" in response["error"].lower()

    def test_archivo_invalido_retorna_error(self, test_app):
        """Rechaza archivos que no son PDF"""

        with test_app.app_context():
            data = ImmutableMultiDict([
                ("new_titulo", "Test Libro"),
                ("new_isbn", "123")
            ])

            mock_file = MagicMock()
            mock_file.filename = "test.txt"
            archivo = {"pdf": mock_file}

            response, status = agregar_libro_service(data, archivo)

            assert status == 400
            assert "error" in response
            assert "PDF" in response["error"]

    def test_agregar_libro_exitoso(self, test_app):
        """Agrega libro correctamente"""


        with (
            patch('app.api.libros.services.UPLOAD_FOLDER', '/tmp'),
            patch('app.api.libros.services.db') as mock_db,
            patch('app.api.libros.services.Libros') as mock_libros_class,
            patch('app.api.libros.services.Autores') as mock_autores,
            patch('app.api.libros.services.Carreras') as mock_carreras,
            patch('app.api.libros.services.generar_slug') as mock_generar_slug,
        ):
            # Mocks base
            mock_session = MagicMock()
            mock_db.session = mock_session

            mock_generar_slug.side_effect = ["test-libro", "test-libro-1"]

            mock_libro = MagicMock()
            mock_libro.id_libro = 1
            mock_libro.titulo = "Test Libro"
            mock_libro.slug_titulo = "test-libro-1"
            mock_libro.autores = []
            mock_libro.carreras = []
            mock_libro.to_dict.return_value = {
                "id_libro": 1,
                "titulo": "Test Libro",
                "isbn": "123456",
                "autores": [],
                "carreras": []
            }
            mock_libros_class.return_value = mock_libro

            mock_autores.query.filter.return_value.all.return_value = []
            mock_carreras.query.filter.return_value.all.return_value = []

            # Datos simulados del form
            data = ImmutableMultiDict([
                ("new_titulo", "Test Libro"),
                ("new_isbn", "123456"),
                ("new_estado", "disponible"),
                ("new_anio_publicacion", "2024"),
                ("new_id_autor", ""),
                ("new_id_carrera", "")
            ])

            mock_pdf = MagicMock()
            mock_pdf.filename = "test.pdf"
            mock_pdf.save = MagicMock()
            archivo = {"pdf": mock_pdf}

            # Contexto Flask de request
            with test_app.test_request_context('/', method='POST', data=data):
                response, status = agregar_libro_service(data, archivo)

                assert status == 201
                assert response["mensaje"] == "Libro agregado correctamente"
                assert "libro" in response

                mock_session.flush.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_pdf.save.assert_called_once()

    def test_agregar_libro_variantes(self, test_app):
        """Prueba todas las variantes del flujo de agregar_libro_service pa llegar a 100%"""

        with test_app.app_context():
            with (
                patch('app.api.libros.services.db') as mock_db,
                patch('app.api.libros.services.Libros') as mock_libros_class,
                patch('app.api.libros.services.Autores') as mock_autores,
                patch('app.api.libros.services.Carreras') as mock_carreras,
                patch('app.api.libros.services.generar_slug') as mock_generar_slug,
            ):
                mock_session = MagicMock()
                mock_db.session = mock_session

                mock_pdf = MagicMock()
                mock_pdf.filename = "test.pdf"
                mock_pdf.save = MagicMock()
                archivo = {"pdf": mock_pdf}

                # Caso 1: múltiples autores y carreras (getlist)

                print("\nCaso 1: Múltiples autores via getlist")
                mock_autor1, mock_autor2 = MagicMock(
                    id_autor=1), MagicMock(id_autor=2)
                mock_autores.query.filter.return_value.all.return_value = [
                    mock_autor1, mock_autor2]
                mock_carrera = MagicMock(id_carrera=1)
                mock_carreras.query.filter.return_value.all.return_value = [
                    mock_carrera]

                data = ImmutableMultiDict([
                    ("new_titulo", "Libro A"),
                    ("new_isbn", "111"),
                    ("new_id_autor", "1"),
                    ("new_id_autor", "2"),
                    ("new_id_carrera", "1")
                ])
                data.getlist = lambda k: [
                    "1", "2"] if k == "new_id_autor" else []

                response, status = agregar_libro_service(data, archivo)
                assert status == 201, f"Caso 1 falló: {response}"
                assert response["mensaje"] == "Libro agregado correctamente"

                # Resetear mocks, para que no se confunda y poder unificar tests
                mock_autores.reset_mock()
                mock_carreras.reset_mock()
                mock_session.reset_mock()
                mock_pdf.reset_mock()

                # Caso 2: un solo autor (via get)

                print("\nCaso 2: Un solo autor via get")
                mock_autores.query.filter.return_value.all.return_value = [
                    MagicMock(id_autor=1)]
                mock_carreras.query.filter.return_value.all.return_value = []

                data = ImmutableMultiDict([
                    ("new_titulo", "Libro B"),
                    ("new_isbn", "222"),
                    ("new_id_autor", "1")
                ])
                data.getlist = lambda k: []  # getlist vacío para forzar data.get()

                response, status = agregar_libro_service(data, archivo)
                assert status == 201, f"Caso 2 falló: {response}"

                mock_autores.reset_mock()
                mock_carreras.reset_mock()
                mock_session.reset_mock()
                mock_pdf.reset_mock()

                # Caso 3: carrera como string
                print("\nCaso 3: Carrera como string")
                mock_autores.query.filter.return_value.all.return_value = []
                mock_carreras.query.filter.return_value.all.return_value = [
                    MagicMock(id_carrera=1)]

                data = ImmutableMultiDict([
                    ("new_titulo", "Libro C"),
                    ("new_isbn", "333"),
                    ("new_id_carrera", "1")  # String
                ])
                data.getlist = lambda k: []

                response, status = agregar_libro_service(data, archivo)
                assert status == 201, f"Caso 3 falló: {response}"

                mock_autores.reset_mock()
                mock_carreras.reset_mock()
                mock_session.reset_mock()
                mock_pdf.reset_mock()

                # Caso 4: carrera como int
                print("\nCaso 4: Carrera como int")
                mock_autores.query.filter.return_value.all.return_value = []
                mock_carreras.query.filter.return_value.all.return_value = [
                    MagicMock(id_carrera=1)]

                data = ImmutableMultiDict([
                    ("new_titulo", "Libro D"),
                    ("new_isbn", "444")
                ])
                data.getlist = lambda k: []

                # Mock get para devolver INT
                original_get = data.get
                data.get = lambda k, d=None: 1 if k == "new_id_carrera" else original_get(
                    k, d)

                response, status = agregar_libro_service(data, archivo)
                assert status == 201, f"Caso 4 falló: {response}"

                mock_autores.reset_mock()
                mock_carreras.reset_mock()
                mock_session.reset_mock()
                mock_pdf.reset_mock()

                # Caso 5: carreras como lista

                print("\nCaso 5: Carreras como lista")
                mock_autores.query.filter.return_value.all.return_value = []
                mock_carreras.query.filter.return_value.all.return_value = [
                    MagicMock(id_carrera=1),
                    MagicMock(id_carrera=2)
                ]

                data = ImmutableMultiDict([
                    ("new_titulo", "Libro E"),
                    ("new_isbn", "555")
                ])
                data.getlist = lambda k: []

                # Mock get para devolver LISTA
                data.get = lambda k, d=None: [
                    "1", "2"] if k == "new_id_carrera" else original_get(k, d)

                response, status = agregar_libro_service(data, archivo)
                assert status == 201, f"Caso 5 falló: {response}"

                mock_autores.reset_mock()
                mock_carreras.reset_mock()
                mock_session.reset_mock()
                mock_pdf.reset_mock()

                # Caso 6: Primera llamada a get() devuelve None, segunda devuelve "1"
                print("\nCaso 6: Carrera devuelta en segunda llamada a get()")

                mock_autores.query.filter.return_value.all.return_value = []
                mock_carreras.query.filter.return_value.all.return_value = [
                    MagicMock(id_carrera=1)
                ]

                data = ImmutableMultiDict([
                    ("new_titulo", "Libro F"),
                    ("new_isbn", "666"),
                    ("new_id_carrera", "1")
                ])
                data.getlist = lambda k: []  # Simula lista vacía

                # Simula el patrón: primera llamada devuelve None, segunda devuelve "1"
                call_count = {'count': 0}
                original_get = data.get

                def mock_get(key, default=None):
                    if key == "new_id_carrera":
                        call_count['count'] += 1
                        if call_count['count'] == 1:
                            return None  # primera llamada -> None
                        else:
                            return "1"   # segunda llamada -> valor
                    return original_get(key, default)

                data.get = mock_get

                response, status = agregar_libro_service(data, archivo)
                assert status == 201, f"Caso 6 falló: {response}"
                mock_carreras.query.filter.assert_called_once()

                print("\nTodos los casos pasaron!")

    def test_agregar_libro_fallido(self, test_app):
        """Errores"""

        with test_app.app_context():
            with patch('app.api.libros.services.db') as mock_db:
                mock_db.session.commit.side_effect = Exception("DB Error")

                data = ImmutableMultiDict([
                    ("new_titulo", "Test"),
                    ("new_isbn", "123")
                ])

                archivo = {}

                response, status = agregar_libro_service(data, archivo)

                assert status == 500
                assert "error" in response
                mock_db.session.rollback.assert_called_once()

# actualizar_libro_service()


class TestActualizarLibroService:
    """Tests para actualizar_libro_service"""

    def test_libro_no_encontrado(self, test_app):
        """Retorna 401(no recibió datos validos para el recurso solicitado) si libro no existe"""

        with test_app.app_context():
            with patch('app.api.libros.services.Libros') as mock_libros:
                mock_libros.query.get.return_value = None

                data = ImmutableMultiDict([("edit_titulo", "Test")])
                archivo = {}

                response, status = actualizar_libro_service(999, data, archivo)

                assert response == {'error': 'Libro no encontrado'}
                assert status == 404

    def test_actualizar_titulo(self, test_app):
        """Actualiza el título del libro"""

        with test_app.app_context():
            with patch('app.api.libros.services.db') as mock_db, \
                    patch('app.api.libros.services.generar_slug') as mock_generar_slug, \
                    patch('app.api.libros.services.Libros') as mock_libros:

                # Configuración de mocks
                mock_generar_slug.return_value = "nuevo-titulo-1"
                mock_session = MagicMock()
                mock_db.session = mock_session

                # Mock libro existente
                mock_libro = MagicMock()
                mock_libro.id_libro = 1
                mock_libro.titulo = "Original"
                mock_libro.autores = []
                mock_libro.carreras = []
                mock_libro.to_dict.return_value = {
                    "id_libro": 1,
                    "titulo": "Nuevo Título"
                }

                mock_libros.query.get.return_value = mock_libro

                # Datos de prueba
                data = ImmutableMultiDict([("edit_titulo", "Nuevo Título")])
                archivo = {}

                # Ejecutar servicio
                response, status = actualizar_libro_service(1, data, archivo)

                # Verificaciones
                assert status == 200
                assert response["mensaje"] == "Libro actualizado correctamente"
                assert mock_libro.titulo == "Nuevo Título"
                mock_session.commit.assert_called_once()


    def test_actualizar_error_database(self, test_app):
        """Maneja errores de base de datos"""

        with test_app.app_context():
            with patch('app.api.libros.services.db') as mock_db:
                mock_db.session.commit.side_effect = Exception("DB Error")

                with patch('app.api.libros.services.Libros') as mock_libros:
                    mock_libro = MagicMock()
                    mock_libros.query.get.return_value = mock_libro

                    data = ImmutableMultiDict([("edit_titulo", "Test")])
                    archivo = {}

                    response, status = actualizar_libro_service(
                        1, data, archivo)

                    assert status == 401
                    assert "error" in response
                    mock_db.session.rollback.assert_called_once()

# eliminar_libro_serviec()


class TestEliminarLibroService:
    """Test para eliminar_libro_service"""

    def test_eliminar_libro_no_encontrado(self,mocker):
        """Devuelve error cuando el libro no es encontrado"""
        mock_get = mocker.patch("app.api.libros.services.db.session.get",return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            eliminar_libro_service(990)
        
        assert str(exc_info.value) == "Libro con ID 990 no encontrado"
        mock_get.assert_called_once_with(Libros,990)

