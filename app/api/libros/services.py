from app import db
from app.config import Config
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
    autores_ids = data.get("autores_ids", [])
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
    id_libro = str(nuevo_libro.id_libro)
    slug_libro = generar_slug(titulo, id_libro)
    nuevo_libro.slug_titulo = slug_libro
    db.session.commit()
    
    # Agregar registro a la tabla de asociación libros_autores si se proporciona id_autor
    if autores_ids:
        for autor_id in autores_ids:
            autor = Autores.query.get(autor_id)
            if autor:
                nuevo_libro.autores.append(autor)
    
    return jsonify({'mensaje': 'Libro agregado correctamente', 'id': nuevo_libro.id_libro, 'slug': slug_libro}), 201