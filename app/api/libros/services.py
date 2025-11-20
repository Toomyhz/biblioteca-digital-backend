"""
Services de libros; este archivo maneja toda la lógica del "negocio" y las validaciones

para las respuestas que devuelvan las funciones debe ser necesario que sigan
el patrón 

{dict, int}

para que de esa manera la respuesta final, en cualquier excepción o resultado
sea:

{response, status}

"""
from app.extensions import cloud_storage
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
import io
import time
import tempfile

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
    print("\n⏱️ --- INICIO CRONÓMETRO (MODO TEMPFILE) ---")
    inicio_total = time.time()

    # 1. Base de Datos (Igual que antes)
    t_db = time.time()
    
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
    
    # ... (Tus relaciones de autores y carreras siguen igual) ...
    autores_ids = data.get("ids_autores",[])
    if autores_ids:
        nuevo_libro.autores = Autores.query.filter(Autores.id_autor.in_(autores_ids)).all()
    carreras_ids = data.get("ids_carreras", [])
    if carreras_ids:
        nuevo_libro.carreras = Carreras.query.filter(Carreras.id_carrera.in_(carreras_ids)).all()

    db.session.flush()
    nuevo_libro.slug_titulo = generar_slug(titulo, str(nuevo_libro.id_libro))
    db.session.flush()
    print(f"📝 [BD] Metadata guardada: {time.time() - t_db:.4f} seg")

    # Rutas
    pdf_filename = f"{nuevo_libro.slug_titulo}.pdf"
    portada_filename = f"{nuevo_libro.slug_titulo}_portada.jpg" 
    key_pdf = f"libros/{pdf_filename}"
    key_portada = f"portadas/{portada_filename}"
    
    # Variable para guardar la ruta temporal y borrarla luego
    temp_pdf_path = None

    try:
        # 2. Guardar PDF en DISCO TEMPORAL (La clave de la velocidad)
        t_read = time.time()
        pdf_bytes = archivo_pdf.read()
        
        # Creamos un archivo físico temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            temp_pdf_path = tmp.name # Guardamos la ruta ej: C:\Tmp\asd.pdf
            
        tamano_mb = len(pdf_bytes) / (1024 * 1024)
        print(f"💾 [DISCO] PDF guardado temporalmente ({tamano_mb:.2f} MB): {time.time() - t_read:.4f} seg")

        # 3. Procesar Portada (Desde el archivo en disco es más eficiente para fitz)
        t_cpu = time.time()
        doc = fitz.open(temp_pdf_path) 
        page = doc[0]
        matriz = fitz.Matrix(0.3,0.3)
        pix = page.get_pixmap(matrix=matriz,alpha=False)
        portada_bytes = pix.tobytes("jpg")
        doc.close()
        print(f"⚙️ [CPU] Portada generada: {time.time() - t_cpu:.4f} seg")

        # 4. Subida PDF (USANDO LA RUTA DEL DISCO)
        t_up_pdf = time.time()
        print(f"🚀 [RED] Subiendo PDF en PARALELO desde disco...")
        
        # AQUI ESTÁ EL TRUCO: Pasamos el PATH (string), no el BytesIO
        cloud_storage.upload_file(
            temp_pdf_path,  # <--- Pasamos la ruta string
            key_pdf,
            content_type='application/pdf',
            acl='private'
        )
        
        duracion_pdf = time.time() - t_up_pdf
        velocidad = tamano_mb / duracion_pdf if duracion_pdf > 0 else 0
        print(f"✅ [RED] PDF subido en: {duracion_pdf:.2f} seg (Velocidad: {velocidad:.2f} MB/s)")
        
        # 5. Subida Portada (Sigue igual en RAM porque es pequeña)
        t_up_img = time.time()
        cloud_storage.upload_file(
            io.BytesIO(portada_bytes), 
            key_portada, 
            content_type='image/jpg',
            acl='public-read'
        )
        print(f"✅ [RED] Portada subida en: {time.time() - t_up_img:.4f} seg")

    except Exception as e:
        raise ServiceError(f'Error al procesar el PDF: {str(e)}', 400)
    
    finally:
        # LIMPIEZA: Borramos el archivo temporal siempre, pase lo que pase
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            # print("🧹 Archivo temporal eliminado")

    nuevo_libro.archivo_pdf = key_pdf
    nuevo_libro.archivo_portada = key_portada

    print(f"🏁 --- TIEMPO TOTAL: {time.time() - inicio_total:.2f} seg ---\n")
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
        libro.autores = Autores.query.filter(Autores.id_autor.in_(data["ids_autores"])).all()
    if 'ids_carreras' in data:
        libro.carreras = Carreras.query.filter(Carreras.id_carrera.in_(data["ids_carreras"])).all()

    return libro
      
    
def actualizar_libro_archivo_service(id_libro, archivo_pdf):    
    libro = Libros.query.get(id_libro)
    if not libro:
        raise NotFoundError(f'Libro con ID {id_libro} no encontrado.')

    path_pdf_viejo = libro.archivo_pdf
    path_portada_vieja = libro.archivo_portada

    key_pdf = f"libros/{libro.slug_titulo}.pdf"
    key_portada = f"portadas/{libro.slug_titulo}_portada.jpg"

    temp_pdf_path = None

    try:
        pdf_bytes = archivo_pdf.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            temp_pdf_path = tmp.name # Ruta física

        doc = fitz.open(temp_pdf_path)
        page = doc[0]
        matriz = fitz.Matrix(0.3, 0.3) 
        pix = page.get_pixmap(matrix=matriz, alpha=False)
        portada_bytes = pix.tobytes("jpg")
        doc.close()
        cloud_storage.upload_file(
            temp_pdf_path, 
            key_pdf,
            content_type='application/pdf',
            acl='private'
        )

        cloud_storage.upload_file(
            io.BytesIO(portada_bytes), 
            key_portada, 
            content_type='image/jpeg', # Importante: image/jpeg
            acl='public-read'
        )
           
    except Exception as e:
        raise ServiceError(f'Error al procesar el PDF: {str(e)}', 400)

    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
    
    if path_pdf_viejo and path_pdf_viejo != key_pdf:
        print(f"🗑️ Eliminando huérfano: {path_pdf_viejo}")
        cloud_storage.delete_file(path_pdf_viejo)

    if path_portada_vieja and path_portada_vieja != key_portada:
        print(f"🗑️ Eliminando huérfano: {path_portada_vieja}")
        cloud_storage.delete_file(path_portada_vieja)

    libro.archivo_pdf = key_pdf
    libro.archivo_portada = key_portada
    return libro


def eliminar_libro_service(id_libro):
    libro = Libros.query.get(id_libro)
    if not libro:
        raise NotFoundError(f"Libro con ID {id_libro} no encontrado")


    # Eliminar archivo PDF asociado si existe
    if libro.archivo_pdf:
        cloud_storage.delete_file(libro.archivo_pdf)

    if libro.archivo_portada:
        cloud_storage.delete_file(libro.archivo_portada)

    db.session.delete(libro)
    return libro