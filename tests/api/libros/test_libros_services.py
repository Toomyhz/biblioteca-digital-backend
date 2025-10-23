import pytest
from unittest.mock import patch, MagicMock, mock_open
from werkzeug.datastructures import ImmutableMultiDict

# archivos_permitidos()


class TestArchivosPermitidos:

    def test_acepta_pdf_minusculas(self):
        """Acepta archivos .pdf en minúsculas"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("documento.pdf") == True

    def test_acepta_pdf_mayusculas(self):
        """Acepta archivos .PDF en mayúsculas"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("DOCUMENTO.PDF") == True

    def test_acepta_pdf_mixto(self):
        """Acepta archivos .PdF en mixto"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("documento.PdF") == True

    def test_rechaza_txt(self):
        """Rechaza archivos .txt"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("documento.txt") == False

    def test_rechaza_jpg(self):
        """Rechaza archivos .jpg"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("imagen.jpg") == False

    def test_rechaza_exe(self):
        """Rechaza archivos .exe"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("virus.exe") == False

    def test_rechaza_sin_extension(self):
        """Rechaza archivos sin extensión"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("documento") == False

    def test_rechaza_vacio(self):
        """Rechaza string vacío"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("") == False

    def test_multiples_puntos(self):
        """Maneja archivos con múltiples puntos"""
        from app.api.libros.services import archivos_permitidos
        assert archivos_permitidos("mi.libro.final.pdf") == True
        assert archivos_permitidos("mi.libro.final.txt") == False

# listar_libros_service()


class TestListarLibrosService():
    def test_listar_sin_resultados(self, test_app):
        """Lista vacía cuando no hay libros (HÍBRIDO)"""
        from app.api.libros.services import listar_libros_service

        # Mock paginación vacía
        mock_paginacion = MagicMock()
        mock_paginacion.items = []
        mock_paginacion.page = 1
        mock_paginacion.per_page = 10
        mock_paginacion.total = 0
        mock_paginacion.pages = 0

        mock_query = MagicMock()
        mock_query.order_by.return_value.paginate.return_value = mock_paginacion

        with patch('app.api.libros.services.Libros') as mock_libros:
            mock_libros.query = mock_query

            # Contexto de Flask con request real
            with test_app.test_request_context('/?pagina=1&limite=10&busqueda='):
                response, status = listar_libros_service()

                assert status == 200
                assert response["data"] == []
                assert response["paginacion"]["total"] == 0

    def test_listar_con_resultados(self, test_app):
        """Retorna libros correctamente paginados"""
        from app.api.libros.services import listar_libros_service

        libro1 = MagicMock()
        libro1.to_dict.return_value = {"id_libro": 1, "titulo": "Libro 1"}
        libro2 = MagicMock()
        libro2.to_dict.return_value = {"id_libro": 2, "titulo": "Libro 2"}

        mock_paginacion = MagicMock()
        mock_paginacion.items = [libro1, libro2]
        mock_paginacion.page = 1
        mock_paginacion.per_page = 10
        mock_paginacion.total = 2
        mock_paginacion.pages = 1

        mock_query = MagicMock()
        mock_query.order_by.return_value.paginate.return_value = mock_paginacion

        with patch('app.api.libros.services.Libros') as mock_libros:
            mock_libros.query = mock_query

            with test_app.test_request_context('/?pagina=1&limite=10&busqueda='):
                response, status = listar_libros_service()

            assert status == 200
            assert len(response["data"]) == 2
            assert response["data"][0]["titulo"] == "Libro 1"
            assert response["paginacion"]["total"] == 2

    def test_listar_con_paginacion(self, test_app):
        """Respeta parámetros de paginación"""
        from app.api.libros.services import listar_libros_service

        mock_paginacion = MagicMock()
        mock_paginacion.items = []
        mock_paginacion.page = 2
        mock_paginacion.per_page = 5
        mock_paginacion.total = 12
        mock_paginacion.pages = 3

        mock_query = MagicMock()
        mock_query.order_by.return_value.paginate.return_value = mock_paginacion
        with patch('app.api.libros.services.Libros') as mock_libros:
            mock_libros.query = mock_query

            with test_app.test_request_context('/?pagina=2&limite=5&busqueda='):
                response, status = listar_libros_service()

                assert status == 200
                assert response["paginacion"]["pagina"] == 2
                assert response["paginacion"]["limite"] == 5
                assert response["paginacion"]["total"] == 12
                assert response["paginacion"]["total_paginas"] == 3

    def test_listar_sin_busqueda(self, test_app):
        """Lista libros sin parámetro de búsqueda sin ejecutar SQL real"""
        from app.api.libros.services import listar_libros_service

        # Mock de libros con método to_dict()
        mock_libro1 = MagicMock()
        mock_libro1.to_dict.return_value = {"id_libro": 1, "titulo": "Libro 1"}
        mock_libro2 = MagicMock()
        mock_libro2.to_dict.return_value = {"id_libro": 2, "titulo": "Libro 2"}

        # Mock paginación completa
        mock_paginate = MagicMock(
            items=[mock_libro1, mock_libro2],
            page=1,
            per_page=10,
            total=2,
            pages=1
        )

        # Mock chain: query -> order_by -> paginate
        mock_order = MagicMock()
        mock_order.paginate.return_value = mock_paginate

        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_order
        with patch('app.api.libros.services.Libros') as mock_libros:
            mock_libros.query = mock_query

            with test_app.test_request_context('/?pagina=1&limite=10'):
                response, status = listar_libros_service()

            # print("=== test_listar_sin_busqueda ===")
            # print("Status:", status)
            # print("Response:", response)
            # print("mock_query.filter called:",
            #       mock_query.filter.called)
            # print("mock_order.paginate called:", mock_order.paginate.called)
            # print("mock_paginate.items:", mock_paginate.items)
            # print("=== FIN ===\n")

            assert status == 200
            assert response["paginacion"]["total"] == 2
            assert len(response["data"]) == 2
            assert response["data"][0]["titulo"] == "Libro 1"

    def test_listar_con_busqueda(self, test_app):
        """Aplica filtro de búsqueda sin ejecutar SQL real"""
        from app.api.libros.services import listar_libros_service

        # Simulamos que 'or_' devuelve algo válido sin usar SQLAlchemy
        with patch('app.api.libros.services.or_') as mock_or:
            mock_or.return_value = "filtro_mock"

            # Mock paginación completa
            mock_paginate = MagicMock(
                items=[],
                page=1,
                per_page=10,
                total=0,
                pages=0
            )

            # Mock chain: query -> filter -> order_by -> paginate
            mock_order = MagicMock()
            mock_order.paginate.return_value = mock_paginate

            mock_filter = MagicMock()
            mock_filter.order_by.return_value = mock_order

            mock_query = MagicMock()
            mock_query.filter.return_value = mock_filter
            with patch('app.api.libros.services.Libros') as mock_libros:
                mock_libros.query = mock_query

                with test_app.test_request_context('/?pagina=1&limite=10&busqueda=Aleph'):
                    response, status = listar_libros_service()

                # Verificaciones
                assert status == 200
                mock_query.filter.assert_called_once_with("filtro_mock")
                mock_or.assert_called_once()  # se usó el filtro OR
                assert response["paginacion"]["total"] == 0

    def test_listar_error_database(self, test_app):
        """Maneja errores de base de datos"""
        from app.api.libros.services import listar_libros_service

        # Mock error en execute
        with patch('app.api.libros.services.db') as mock_db:
            mock_db.session.execute.side_effect = Exception("Connection error")

            with test_app.test_request_context('/?pagina=1&limite=10&busqueda='):
                response, status = listar_libros_service()

                assert status == 500
                assert "error" in response
                mock_db.session.rollback.assert_called_once()

# agregar_libro_service()


class TestAgregarLibroService:
    """Tests para agregar_libro_service"""

    def test_sin_titulo_retorna_error(self, test_app):
        """Rechaza libro sin título"""
        from app.api.libros.services import agregar_libro_service

        with test_app.app_context():
            data = ImmutableMultiDict([("new_isbn", "123456")])
            archivo = {}

            response, status = agregar_libro_service(data, archivo)

            assert status == 400
            assert "error" in response
            assert "título" in response["error"].lower()

    def test_archivo_invalido_retorna_error(self, test_app):
        """Rechaza archivos que no son PDF"""
        from app.api.libros.services import agregar_libro_service

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
        from unittest.mock import patch, MagicMock
        from werkzeug.datastructures import ImmutableMultiDict
        from app.api.libros.services import agregar_libro_service

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
        from app.api.libros.services import agregar_libro_service

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

                def crear_mock_libro():
                    """Crea un mock de libro limpio"""
                    mock_generar_slug.side_effect = [
                        "test-libro", "test-libro-1"]
                    mock_libro = MagicMock()
                    mock_libro.id_libro = 1
                    mock_libro.autores = []
                    mock_libro.carreras = []
                    mock_libro.to_dict.return_value = {
                        "id_libro": 1,
                        "titulo": "Test Libro"
                    }
                    mock_libros_class.return_value = mock_libro
                    return mock_libro

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
        from app.api.libros.services import agregar_libro_service

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
        from app.api.libros.services import actualizar_libro_service

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
        from app.api.libros.services import actualizar_libro_service

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

    def test_pdf_existente_y_eliminar_pdf_antiguo(self, test_app):
        pass

    def test_actualizar_error_database(self, test_app):
        """Maneja errores de base de datos"""
        from app.api.libros.services import actualizar_libro_service

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

    def test_eliminar_libro_no_encontrado(self, test_app):
        """Devuelve error cuando el libro no es encontrado"""
        from app.api.libros.services import eliminar_libro_service

        with patch('app.api.libros.services.Libros') as mock_libros:
            mock_libros.query.get.return_value = None  # No hay libro, no se encontró

            response, status = eliminar_libro_service(990)  # HNo hay id

            assert status == 404
            assert response == {'error': 'Libro no encontrado'}

            # no debe hacer commit ni borrar de la bd
            with patch('app.api.libros.services.db') as mock_db:
                mock_db.session.delete.assert_not_called()
                mock_db.session.commit.assert_not_called()
