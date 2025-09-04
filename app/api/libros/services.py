from app import db
from app.models.libros import Libro
from app.config import Config
from app.api.utils.helpers import generar_slug
from werkzeug.utils import secure_filename
from flask import jsonify
import os

def agregar_libro_service(data, archivo):
    if not archivo or archivo.filename == '':
            return jsonify({'error': 'Archivo PDF requerido'}), 400
 
    filename = secure_filename(archivo.filename)
    ruta_relativa = f'libros_pdf/{filename}'
    slug = generar_slug(data.get("new_titulo"))
            # Crear y guardar el libro en la base de datos
    nuevo_libro = Libro(
        titulo=data.get("new_titulo"),
        autor=data.get("new_autor"),
        anio_publicacion=data.get("new_anio"),
        carrera=data.get("new_carrera"),
        estado=data.get("new_estado"),
        archivo_pdf=ruta_relativa,
        slug=slug
    )
    db.session.add(nuevo_libro)
    db.session.commit()
    
    archivo.save(os.path.join(Config.UPLOAD_FOLDER, filename))

    return jsonify({'mensaje': 'Libro subido correctamente', 'slug': slug}), 201