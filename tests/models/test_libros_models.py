import pytest
from sqlalchemy.exc import IntegrityError
from app.models.libros import Libros
from app.api.utils.helpers import generar_slug

def test_creacion_usuarios(test_db):
    """
    Prueba 2:Verifica la creación y guardado exitoso de un libro.
    """
    datos_libro = {
        "titulo":"Star Wars 2: La Guerra De Los Clones", 
        "isbn":"008207346",
        "anio_publicacion": 1978,
        "archivo_pdf": "Test.pdf"
    }
    new_libro = Libros(
        titulo=datos_libro["titulo"],
        isbn = datos_libro["isbn"],
        anio_publicacion = datos_libro["anio_publicacion"],
        archivo_pdf = datos_libro["archivo_pdf"],
        slug_titulo = generar_slug(datos_libro["titulo"])
    )
    test_db.session.add(new_libro)
    test_db.session.commit()


    