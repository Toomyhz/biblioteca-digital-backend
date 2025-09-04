from app import db
from app.config import Config
from app.api.utils.helpers import generar_slug
from werkzeug.utils import secure_filename
from flask import jsonify
import os

def agregar_libro_service(data, archivo):
    campos_requeridos = ["new_titulo", "new_autor", "new_anio", "new_carrera", "new_estado"]    
    for campo in campos_requeridos:
        if not data.get(campo):
                return jsonify({'error': f'El campo {campo} es obligatorio'}), 400
    if not archivo or archivo.filename == '':
        return jsonify({'error': 'El archivo PDF es obligatorio'}), 400
    
    filename = secure_filename(archivo.filename)
    slug = generar_slug(data.get("new_titulo"))
    ruta_relativa = f'libros_pdf/{slug}_{filename}'
    
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al subir el libro', 'detalle': str(e)}), 500