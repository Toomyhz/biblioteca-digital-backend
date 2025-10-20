import pytest
from unittest.mock import patch, MagicMock, Mock, call, mock_open
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from io import BytesIO
import os

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
    @patch('app.api.libros.services.db')
    @patch('app.api.libros.services.Libros')
    def test_listar_sin_resultados(self, mock_libros, mock_db, test_app):
        """Lista vacía cuando no hay libros"""
        from app.api.libros.services import listar_libros_service
        # mock paginación vacía
        mock_paginacion = MagicMock()
        mock_paginacion.items = []
        mock_paginacion.page = 1
        mock_paginacion.per_page = 10
        mock_paginacion.total = 0
        mock_paginacion.pages = 0

        mock_query = MagicMock()
        mock_query.order_by.return_value.paginate.return_value = mock_paginacion
        mock_libros.query = mock_query

        with test_app.test_request_context('/libros?pagina=1&limite=10&busqueda='):

            response, status = listar_libros_service()

            assert status == 200
            assert response["data"] == []
            assert response["paginacion"]["total"] == 0

    def test_listar_con_resultados():
        pass
