"""
Services de libros; este archivo maneja toda la lógica del "negocio" y las validaciones

para las respuestas que devuelvan las funciones debe ser necesario que sigan
el patrón 

{dict, int}

para que de esa manera la respuesta final, en cualquier excepción o resultado
sea:

{response, status}

"""

from app import db
from app.config import Config
from app.models.carreras import Carreras
from app.models.libros import Libros
from app.models.autores import Autores
from app.api.utils.helpers import generar_slug
from flask import request, jsonify, current_app
from sqlalchemy import or_, text, func, literal, desc
import os
from app.api.exceptions import NotFoundError, ServiceError
import fitz
import uuid

UPLOAD_FOLDER = Config.PDF_UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

# Funcion para evitar subir archivos que no sean pdf
def archivos_permitidos(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def listar_libros_service(pagina, limite, busqueda):
    try:
        # Para Oracle
        db.session.execute(text("ALTER SESSION SET NLS_COMP = LINGUISTIC"))
        db.session.execute(text("ALTER SESSION SET NLS_SORT = BINARY_AI"))

        query = Libros.query

        if busqueda:
            # Normalizar búsqueda (sin espacios, minúsculas)
            busqueda_normalizada = busqueda.replace(" ", "").lower()
            busqueda_pattern = f"%{busqueda_normalizada}%"

            # Filtros de búsqueda
            query = query.filter(
                or_(
                    # Buscar en título
                    func.lower(func.replace(Libros.titulo, literal(
                        ' '), literal(''))).like(busqueda_pattern),

                    # Buscar en ISBN
                    func.lower(func.replace(Libros.isbn, literal(
                        ' '), literal(''))).like(busqueda_pattern),

                    # Buscar en año (convertir a string)
                    func.to_char(Libros.anio_publicacion).like(
                        f"%{busqueda}%"),

                    # Buscar en autores relacionados
                    Libros.autores.any(
                        func.lower(func.replace(Autores.nombre_completo, literal(
                            ' '), literal(''))).like(busqueda_pattern)
                    ),

                    # Buscar en carreras relacionadas
                    Libros.carreras.any(
                        func.lower(func.replace(Carreras.nombre_carrera, literal(
                            ' '), literal(''))).like(busqueda_pattern)
                    )
                )
            )

        paginacion = query.order_by(Libros.id_libro.desc()).paginate(
            page=pagina, per_page=limite, error_out=False
        )

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

    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'error': f'Error al listar libros: {str(e)}'}, 500


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

    # Agregar registro a la tabla de asociación libros_autores si se proporciona id_autor
    autores_ids = data.get("ids_autores",[])
    if autores_ids:
        nuevo_libro.autores = Autores.query.filter(Autores.id_autor.in_(autores_ids)).all()

    # Agregar registro a la tabla de asociación libros_careras si se proporciona id_carrera
    carreras_ids = data.get("ids_carreras", [])
    if carreras_ids:
        nuevo_libro.carreras = Carreras.query.filter(Carreras.id_carrera.in_(carreras_ids)).all()

    db.session.flush()

    # Cambiar Slug con id
    nuevo_libro.slug_titulo = generar_slug(titulo, str(nuevo_libro.id_libro))

    db.session.flush()

    pdf_filename = f"{nuevo_libro.slug_titulo}.pdf"
    portada_filename = f"{nuevo_libro.slug_titulo}_portada.png"
    
    pdf_folder = current_app.config['PDF_UPLOAD_FOLDER']
    portada_folder = current_app.config['PORTADA_UPLOAD_FOLDER']
    os.makedirs(pdf_folder, exist_ok=True) 
    os.makedirs(portada_folder, exist_ok=True) 
    
    pdf_path = os.path.join(pdf_folder, pdf_filename)
    portada_path = os.path.join(portada_folder, portada_filename)

    # 3. Leer el PDF en memoria
    try:
        pdf_bytes = archivo_pdf.read()
    except Exception as e:
        raise ServiceError(f'No se pudo leer el archivo: {str(e)}', 400)

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=300)
        pix.save(portada_path)
        doc.close()
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)

    except Exception as e:
        # Si PyMuPDF falla (ej. PDF corrupto), limpia los archivos creados
        if os.path.exists(portada_path):
            os.remove(portada_path)
        raise ServiceError(f'Error al procesar el PDF: {str(e)}', 400)
        
    nuevo_libro.archivo_pdf = pdf_filename
    nuevo_libro.archivo_portada = portada_filename

    return nuevo_libro


def obtener_libro_service(id_libro):
    """
    Servicio para obtener un libro por ID
    """

    libro = Libros.query.get(id_libro)
    
    if not libro:
        raise NotFoundError(f'Libro con ID {id_libro} no encontrado.')
        
    return libro

def actualizar_libro_metadata_service(id_libro, data):
    libro = Libros.query.get(id_libro)
    if not libro:
        raise NotFoundError(f"Libro con ID {id_libro} no encontrado")

    pdf_folder = current_app.config["PDF_UPLOAD_FOLDER"]
    portada_folder = current_app.config["PORTADA_UPLOAD_FOLDER"]

    plan_filesystem = None
    
    if "titulo" in data and data["titulo"] != libro.titulo:
        nuevo_titulo = data["titulo"]
        nuevo_slug = generar_slug(nuevo_titulo,str(id_libro))

        path_pdf_antiguo = os.path.join(pdf_folder, libro.archivo_pdf) if libro.archivo_pdf else None
        path_portada_antigua = os.path.join(portada_folder, libro.archivo_portada) if libro.archivo_portada else None

        nuevo_pdf_filename = f"{nuevo_slug}.pdf"
        nueva_portada_filename = f"{nuevo_slug}_cover.png"

        path_pdf_nuevo = os.path.join(pdf_folder, nuevo_pdf_filename)
        path_portada_nueva = os.path.join(portada_folder, nueva_portada_filename)
        
        plan_filesystem = {
            "archivos_a_renombrar":[
                (path_pdf_antiguo,path_pdf_nuevo),(path_portada_antigua,path_portada_nueva)
            ]
        }

        # 2. Actualizar el modelo con los NUEVOS nombres
        libro.titulo = nuevo_titulo
        libro.slug_titulo = nuevo_slug
        libro.archivo_pdf = nuevo_pdf_filename
        libro.archivo_portada = nueva_portada_filename

    if 'isbn' in data:
        libro.isbn = data['isbn']
    if 'anio_publicacion' in data:
        libro.anio_publicacion = data['anio_publicacion']
    if 'estado' in data:
        libro.estado = data['estado']
    
    if 'ids_autores' in data:
        libro.autores = Autores.query.filter(Autores.id_autor.in_(data["ids_autores"])).all()
    if 'ids_carreras' in data:
        libro.carreras = Carreras.query.filter(Carreras.id_carrera.in_(data["ids_carreras"])).all()

    return libro, plan_filesystem
      
    
def actualizar_libro_archivo_service(id_libro, archivo_pdf):    
    libro = Libros.query.get(id_libro)
    if not libro:
        raise NotFoundError(f'Libro con ID {id_libro} no encontrado.')

    pdf_folder = current_app.config['PDF_UPLOAD_FOLDER']
    portada_folder = current_app.config['PORTADA_UPLOAD_FOLDER']
    

    slug_base = libro.slug_titulo
    pdf_filename_final = f"{slug_base}.pdf"
    portada_filename_final = f"{slug_base}_cover.png"

    path_pdf_antiguo = os.path.join(pdf_folder, libro.archivo_pdf) if libro.archivo_pdf else None
    path_portada_antigua = os.path.join(portada_folder, libro.archivo_portada) if libro.archivo_portada else None

    random_suffix = uuid.uuid4().hex[:8] # String aleatorio
    pdf_filename_temp = f"{slug_base}_{random_suffix}.tmp.pdf"
    portada_filename_temp = f"{slug_base}_{random_suffix}.tmp.png"

    path_pdf_temp = os.path.join(pdf_folder, pdf_filename_temp)
    path_portada_temp = os.path.join(portada_folder, portada_filename_temp)

    try:
        pdf_bytes = archivo_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=150)
        pix.save(path_portada_temp)
        doc.close()
        
        with open(path_pdf_temp, 'wb') as f:
            f.write(pdf_bytes)
            
    except Exception as e:
            # Si la escritura del NUEVO archivo falla, limpiamos los .tmp
            if os.path.exists(path_portada_temp): os.remove(path_portada_temp)
            if os.path.exists(path_pdf_temp): os.remove(path_pdf_temp)
            raise ServiceError(f'Error al procesar el PDF: {str(e)}', 400)

    libro.archivo_pdf = pdf_filename_final
    libro.archivo_portada = portada_filename_final

    plan_filesystem = {
        "antiguos_a_borrar": [p for p in [path_pdf_antiguo, path_portada_antigua] if p],
        "temporales_a_renombrar": [
            (path_pdf_temp, os.path.join(pdf_folder, pdf_filename_final)),
            (path_portada_temp, os.path.join(portada_folder, portada_filename_final))
        ],
        "temporales_a_borrar_en_fallo": [path_pdf_temp, path_portada_temp]
    }
    
    return libro, plan_filesystem


def eliminar_libro_service(id_libro):
    libro = Libros.query.get(id_libro)
    if not libro:
        raise NotFoundError(f"Libro con ID {id_libro} no encontrado")

    pdf_folder = current_app.config["PDF_UPLOAD_FOLDER"]
    portada_folder = current_app.config["PORTADA_UPLOAD_FOLDER"]

    # Eliminar archivo PDF asociado si existe
    if libro.archivo_pdf:
        pdf_path = os.path.join(pdf_folder, libro.archivo_pdf)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


    if libro.archivo_portada:
        pdf_path = os.path.join(portada_folder, libro.archivo_portada)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    db.session.delete(libro)
    return libro