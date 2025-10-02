from app import db
from app.config import Config
from app.models.carreras import Carreras
from app.models.libros import Libros
from app.models.autores import Autores
from app.api.utils.helpers import generar_slug
from flask import request
from sqlalchemy import or_, text, func, literal
import os

UPLOAD_FOLDER = Config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

# Funcion para evitar subir archivos que no sean pdf
def archivos_permitidos(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def listar_libros_service():
    try:
        pagina = request.args.get("pagina", 1, type=int)
        limite = request.args.get("limite", 10, type=int)
        busqueda = request.args.get("busqueda", "", type=str)

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
                    func.lower(func.replace(Libros.titulo, literal(' '), literal(''))).like(busqueda_pattern),
                    
                    # Buscar en ISBN
                    func.lower(func.replace(Libros.isbn, literal(' '), literal(''))).like(busqueda_pattern),
                    
                    # Buscar en año (convertir a string)
                    func.to_char(Libros.anio_publicacion).like(f"%{busqueda}%"),
                    
                    # Buscar en autores relacionados
                    Libros.autores.any(
                        func.lower(func.replace(Autores.nombre_completo, literal(' '), literal(''))).like(busqueda_pattern)
                    ),
                    
                    # Buscar en carreras relacionadas
                    Libros.carreras.any(
                        func.lower(func.replace(Carreras.nombre_carrera, literal(' '), literal(''))).like(busqueda_pattern)
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
        }, 200
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'error': f'Error al listar libros: {str(e)}'}, 500


def agregar_libro_service(data, archivo):
    try:
        titulo = data.get("new_titulo")
        isbn = data.get("new_isbn")
        anio_publicacion = data.get("new_anio_publicacion")
        estado = data.get("new_estado")
        slug_inicial = generar_slug(titulo) if titulo else "slug-temporal"

        if not titulo:
            return {'error': 'El título es obligatorio'}, 400

        pdf_filename = None
        if 'pdf' in archivo:
            pdf_file = archivo['pdf']
            if pdf_file and pdf_file.filename and archivos_permitidos(pdf_file.filename):
                pdf_filename = f"{isbn}_{slug_inicial}.pdf" if isbn else f"{slug_inicial}.pdf"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                pdf_file.save(os.path.join(UPLOAD_FOLDER, pdf_filename))
                
            else:
                return {'error': 'Archivo no permitido, solo se permiten PDFs'}, 400

        nuevo_libro = Libros(
            titulo=titulo,
            isbn=isbn,
            estado=estado,
            anio_publicacion=anio_publicacion,
            archivo_pdf=pdf_filename,
            slug_titulo=slug_inicial
        )

        db.session.add(nuevo_libro)
        db.session.flush()

        # Cambiar Slug con id
        nuevo_libro.slug_titulo = generar_slug(
            titulo, str(nuevo_libro.id_libro))

        # Agregar registro a la tabla de asociación libros_autores si se proporciona id_autor
        autores_ids = data.getlist("new_id_autor")
        if not autores_ids:
            autor_id = data.get("new_id_autor")
            if autor_id:
                autores_ids = [autor_id]
        autores_ids = [int(a) for a in autores_ids if a]

        if autores_ids:
            nuevo_libro.autores = Autores.query.filter(
                Autores.id_autor.in_(autores_ids)
            ).all()

        # Agregar registro a la tabla de asociación libros_careras si se proporciona id_carrera
        carreras_ids = data.get("new_id_carrera")
        if not carreras_ids:
            carrera_id = data.get("new_id_carrera")
            if carrera_id:
                carreras_ids = [carrera_id]
        
        if isinstance(carreras_ids, str):
            carreras_ids = [int(carreras_ids)]
        elif isinstance(carreras_ids, int):
            carreras_ids = [carreras_ids]
        else:
            carreras_ids = [int(c) for c in carreras_ids if c]
        if carreras_ids:
            nuevo_libro.carreras = Carreras.query.filter(
                Carreras.id_carrera.in_(carreras_ids)
            ).all()

        db.session.commit()

        return {
            'mensaje': 'Libro agregado correctamente',
            'libro': nuevo_libro.to_dict()
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al crear libro: {e}'}, 500


def actualizar_libro_service(id_libro, data, archivo):
    try:
        libro = Libros.query.get(id_libro)
        if not libro:
            return None, "Libro no encontrado", 404

        libro.titulo = data.get("edit_titulo", libro.titulo)
        libro.isbn = data.get("edit_isbn", libro.isbn)
        libro.estado = data.get("edit_estado", libro.estado)
        anio = data.get("edit_anio_publicacion")
        if anio:
            libro.anio_publicacion = int(anio)

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
        return {'error': f'Error al actualizar libro: {e}'}, 500


def eliminar_libro_service(id_libro):
    try:
        libro = Libros.query.get(id_libro)
        if not libro:
            return {'error': 'Carrera no encontrada'}, 404

        # Eliminar archivo PDF asociado si existe
        if libro.archivo_pdf:
            pdf_path = os.path.join(UPLOAD_FOLDER, libro.archivo_pdf)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        db.session.delete(libro)
        db.session.commit()

        return {
            'mensaje': 'Libro eliminado correctamente',
            'libro': libro.to_dict()
        }, 200
    
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al eliminar libro: {e}'}, 500
