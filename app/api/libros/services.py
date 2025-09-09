from app import db
from app.config import Config
from app.models.carreras import Carreras
from app.models.libros import Libros
from app.models.autores import Autores
from app.api.utils.helpers import generar_slug
from werkzeug.utils import secure_filename
from flask import jsonify
import os

def agregar_libro_service(data, archivo):
    titulo = data.get("new_titulo")
    isbn = data.get("new_isbn")
    anio_publicacion = data.get("new_anio_publicacion")
    estado = data.get("new_estado")
    filename = secure_filename(archivo.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({'error': 'El archivo debe ser un PDF'}), 400
    
    if not titulo or not estado or not archivo:
        return jsonify({'error': 'Título, estado y archivo son obligatorios'}), 400
    
    slug_libro = generar_slug(titulo)
    archivo_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    archivo.save(archivo_path)
    
    nuevo_libro = Libros(
        titulo=titulo,
        isbn=isbn,
        anio_publicacion=anio_publicacion,
        estado=estado,
        archivo_pdf=archivo_path,
        slug_titulo=slug_libro
    )
    
    db.session.add(nuevo_libro)
    db.session.flush()
    
    # Cambiar Slug con id
    nuevo_libro.slug_titulo = generar_slug(titulo, str(nuevo_libro.id_libro))
    
    # Agregar registro a la tabla de asociación libros_autores si se proporciona id_autor
    autores_ids = data.getlist("autor_id")
    autores_ids = [int(a) for a in autores_ids]
    if autores_ids:
        nuevo_libro.autores = Autores.query.filter(
            Autores.id_autor.in_(autores_ids)
        ).all()

    # Agregar registro a la tabla de asociación libros_careras si se proporciona id_carrera
    carreras_ids = data.get("carrera_id", [])
    if isinstance(carreras_ids, str):
        carreras_ids = [int(carreras_ids)]
    elif isinstance(carreras_ids, int):
        carreras_ids = [carreras_ids]
    if carreras_ids:
        nuevo_libro.carreras = Carreras.query.filter(
            Carreras.id_carrera.in_(carreras_ids)
        ).all()
                
    db.session.commit()
    
    return {'mensaje': 'Libro agregado correctamente', 
            'id': nuevo_libro.id_libro, 
            'slug': nuevo_libro.slug_titulo}, 201

def actualizar_libros_service(id_libro, data):
    libro = Libros.query.get(id_libro)
    if not libro:
        return None, "Libro no encontrado", 404
    
    titulo = data.get("edit_titulo")
    isbn = data.get("edit_isbn")
    anio_publicacion = data.get("edit_anio_publicacion")
    estado = data.get("edit_estado")
    autores_ids = data.get("autores_ids", [])
    carreras_ids = data.get("carreras_ids", [])
    
    if not titulo or not estado:
        return None, "El título y estado son obligatorios", 400
    
    libro.titulo = titulo
    libro.isbn = isbn
    libro.anio_publicacion = anio_publicacion
    libro.estado = estado
    libro.slug_titulo = slug_libro
    libro.autores = [] 
    libro.carreras = []
    
    slug_libro = generar_slug(titulo, id_libro)
    
    autores_ids = data.getlist("autor_id")
    autores_ids = [int(a) for a in autores_ids]
    
    if autores_ids:
        libro.autores = Autores.query.filter(
            Autores.id_autor.in_(autores_ids)
        ).all()

    carreras_ids = data.get("carrera_id", [])
    if isinstance(carreras_ids, str):
        carreras_ids = [int(carreras_ids)]
    elif isinstance(carreras_ids, int):
        carreras_ids = [carreras_ids]
    if carreras_ids:
        libro.carreras = Carreras.query.filter(
            Carreras.id_carrera.in_(carreras_ids)
        ).all()
    
    db.session.commit()
    
    return libro, {'mensaje': 'Libro actualizado correctamente',
                   'titulo': libro.titulo,
                   'slug': libro.slug_titulo
                   }, 200
    
    