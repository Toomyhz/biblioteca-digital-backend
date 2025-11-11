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


def agregar_libro_service(data):
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
    
    return nuevo_libro

def actualizar_archivo_libro_service(id_libro, archivo_pdf):
    libro = Libros.query.get(id_libro)
    if not libro:
        raise NotFoundError(f'Libro con ID {id_libro} no encontrado.')

    slug_base = libro.slug_titulo or f"libro-{libro.id_libro}"
    pdf_filename = f"{slug_base}.pdf"
    portada_filename = f"{slug_base}_portada.png"

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

    # 5. Actualizar el modelo (SIN COMMIT)
    libro.archivo_pdf = pdf_filename
    libro.archivo_portada = portada_filename
    
    # Devuelve el objeto, el controlador hará el commit
    return libro


def actualizar_libro_service(id_libro, data, archivo):
    try:
        libro = Libros.query.get(id_libro)
        if not libro:
            return {'error': 'Libro no encontrado'}, 404

        libro.titulo = data.get("edit_titulo", libro.titulo)
        libro.isbn = data.get("edit_isbn", libro.isbn)
        libro.estado = data.get("edit_estado", libro.estado)
        libro.anio_publicacion = data.get(
            "edit_anio_publicacion", libro.anio_publicacion)
        libro.slug_titulo = generar_slug(libro.titulo, str(libro.id_libro))
        if 'pdf' in archivo:
            pdf_file = archivo['pdf']
            if pdf_file and pdf_file.filename and archivos_permitidos(pdf_file.filename):
                # Eliminar PDF anterior si existe
                if libro.archivo_pdf:
                    old_path = os.path.join(UPLOAD_FOLDER, libro.archivo_pdf)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                # Guardar nuevo PDF
                slug_titulo = generar_slug(libro.titulo)
                pdf_filename = f"{libro.isbn}_{slug_titulo}.pdf" if libro.isbn else f"{slug_titulo}.pdf"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                pdf_file.save(os.path.join(UPLOAD_FOLDER, pdf_filename))
                libro.archivo_pdf = pdf_filename

        autores_ids = data.getlist("edit_id_autor")
        if not autores_ids:
            autor_id = data.get("edit_id_autor")
            if autor_id:
                autores_ids = [autor_id]

        autores_ids = [int(a) for a in autores_ids if a]

        if autores_ids:
            libro.autores = Autores.query.filter(
                Autores.id_autor.in_(autores_ids)
            ).all()
        else:
            libro.autores = []

        carreras_ids = data.getlist("edit_id_carrera")
        if not carreras_ids:
            carrera_id = data.get("edit_id_carrera")
            if carrera_id:
                carreras_ids = [carrera_id]

        if isinstance(carreras_ids, str):
            carreras_ids = [int(carreras_ids)]
        elif isinstance(carreras_ids, int):
            carreras_ids = [carreras_ids]
        else:
            carreras_ids = [int(c) for c in carreras_ids if c]

        if carreras_ids:
            libro.carreras = Carreras.query.filter(
                Carreras.id_carrera.in_(carreras_ids)
            ).all()
        else:
            libro.carreras = []

        db.session.commit()

        return {
            'mensaje': 'Libro actualizado correctamente',
            'libro': libro.to_dict()
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al actualizar libro: {e}'}, 401


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