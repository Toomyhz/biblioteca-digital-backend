from app.extensions import cloud_storage, db
from app.config import Config
from app.models.carreras import Carreras
from app.models.libros import Libros
from app.models.autores import Autores
from app.api.utils.helpers import generar_slug

from sqlalchemy import or_, text, func, literal
import os
from app.api.exceptions import NotFoundError, ServiceError
import fitz
import io
import tempfile
from app.api.libros.utils import procesar_pdf_y_subir

ALLOWED_EXTENSIONS = {'pdf'}

# Funcion para evitar subir archivos que no sean pdf
def archivos_permitidos(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def listar_libros_service(pagina = 1, limite = 10, busqueda = None):

    query = db.session.query(Libros)

    if busqueda:
        # Normalizar búsqueda (sin espacios, minúsculas)
        busqueda_normalizada = busqueda.replace(" ", "").lower()
        busqueda_pattern = f"%{busqueda_normalizada}%"

        # Filtros de búsqueda
        query = query.filter(
            or_(
                # Buscar en título
                func.lower(func.replace(Libros.titulo, literal(' '), literal(''))).like(busqueda_pattern),

                # Buscar en ISBN
                func.lower(func.replace(Libros.isbn, literal(' '), literal(''))).like(busqueda_pattern),

                # Buscar en año (convertir a string)
                func.to_char(Libros.anio_publicacion).like(f"%{busqueda}%"),

                # Buscar en autores relacionados
                Libros.autores.any(
                    func.lower(func.replace(Autores.nombre_completo, literal(' '), literal('')))
                        .like(busqueda_pattern)
                ),

                # Buscar en carreras relacionadas
                Libros.carreras.any(
                    func.lower(func.replace(Carreras.nombre_carrera, literal(' '), literal('')))
                        .like(busqueda_pattern)
                )
            )
        )

    paginacion = query.order_by(Libros.id_libro.desc()).paginate(page=pagina, per_page=limite, error_out=False)

    libros = [libro.to_dict() for libro in paginacion.items]

    return {
        "data": libros,
        "paginacion": {
            "pagina": paginacion.page,
            "limite": paginacion.per_page,
            "total": paginacion.total,
            "total_paginas": paginacion.pages
        }
    }

def agregar_libro_service(data, archivo_pdf):
    titulo = data.get("titulo")
    slug_inicial = generar_slug(titulo)

    nuevo_libro = Libros(
        titulo=titulo,
        isbn=data.get("isbn"),
        estado=data.get("estado"),
        anio_publicacion=data.get("anio_publicacion"),
        slug_titulo=slug_inicial,
        archivo_pdf=None,
        archivo_portada=None,
    )
    db.session.add(nuevo_libro)

    autores_ids = data.get("ids_autores", [])
    if autores_ids:
        nuevo_libro.autores = (
            db.session.query(Autores)
            .filter(Autores.id_autor.in_(autores_ids))
            .all()
        )

    carreras_ids = data.get("ids_carreras", [])
    if carreras_ids:
        nuevo_libro.carreras = (
            db.session.query(Carreras)
            .filter(Carreras.id_carrera.in_(carreras_ids))
            .all()
        )

    db.session.flush()
    nuevo_libro.slug_titulo = generar_slug(titulo, str(nuevo_libro.id_libro))
    db.session.flush()

    # PDF + portada via helper
    key_pdf, key_portada = procesar_pdf_y_subir(archivo_pdf, nuevo_libro.slug_titulo)

    nuevo_libro.archivo_pdf = key_pdf
    nuevo_libro.archivo_portada = key_portada

    return nuevo_libro


def obtener_libro_service(id_libro):
    """
    Servicio para obtener un libro por ID
    """
    libro = db.session.get(Libros, id_libro)
    
    if not libro:
        raise NotFoundError(f'Libro con ID {id_libro} no encontrado.')
        
    return libro

def actualizar_libro_metadata_service(id_libro, data):
    libro = db.session.get(Libros, id_libro)
    if not libro:
        raise NotFoundError(f"Libro con ID {id_libro} no encontrado")
    
    if "titulo" in data and data["titulo"] != libro.titulo:
        nuevo_titulo = data["titulo"]
        nuevo_slug = generar_slug(nuevo_titulo,str(id_libro))

        # 2. Actualizar el modelo con los NUEVOS nombres
        libro.titulo = nuevo_titulo
        libro.slug_titulo = nuevo_slug

    if 'isbn' in data:
        libro.isbn = data['isbn']
    if 'anio_publicacion' in data:
        libro.anio_publicacion = data['anio_publicacion']
    if 'estado' in data:
        libro.estado = data['estado']
    
    if 'ids_autores' in data:
        
        libro.autores = db.session.query(Autores).filter(Autores.id_autor.in_(data["ids_autores"])).all()
    if 'ids_carreras' in data:
        libro.carreras = db.session.query(Carreras).filter(Carreras.id_carrera.in_(data["ids_carreras"])).all()

    return libro
      
    
def actualizar_libro_archivo_service(id_libro, archivo_pdf):
    libro = db.session.get(Libros, id_libro)
    if not libro:
        raise NotFoundError(f"Libro con ID {id_libro} no encontrado.")

    path_pdf_viejo = libro.archivo_pdf
    path_portada_vieja = libro.archivo_portada

    # Usa el slug ya existente
    key_pdf, key_portada = procesar_pdf_y_subir(archivo_pdf, libro.slug_titulo)

    # Borrar archivos antiguos si cambiaron
    if path_pdf_viejo and path_pdf_viejo != key_pdf:
        cloud_storage.delete_file(path_pdf_viejo)

    if path_portada_vieja and path_portada_vieja != key_portada:
        cloud_storage.delete_file(path_portada_vieja)

    libro.archivo_pdf = key_pdf
    libro.archivo_portada = key_portada

    return libro


def eliminar_libro_service(id_libro):
    libro = db.session.get(Libros, id_libro)
    if not libro:
        raise NotFoundError(f"Libro con ID {id_libro} no encontrado")

    # Eliminar archivo PDF asociado si existe
    if libro.archivo_pdf:
        cloud_storage.delete_file(libro.archivo_pdf)

    if libro.archivo_portada:
        cloud_storage.delete_file(libro.archivo_portada)

    db.session.delete(libro)
    return libro