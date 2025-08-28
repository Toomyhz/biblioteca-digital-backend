from flask import Blueprint,request, jsonify
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.book import Book
from app.config import Config
from datetime import datetime

book_bp = Blueprint('books', __name__)

@book_bp.route('/agregar', methods=['POST'])
def agregar_libro():
    if request.method == 'POST':
        new_titulo = request.form.get('titulo-libro')
        new_autor = request.form.get('autor-libro')
        new_carrera = request.form.get('carrera-libro')
        
        new_anio = request.form.get('anio-libro')
        new_estado = request.form.get('estado-libro')
        print(new_estado)
        archivo = request.files.get('archivo-pdf')
        if not archivo or archivo.filename == '':
            return jsonify({'error': 'Archivo PDF requerido'}), 400
        
        if archivo :
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(Config.UPLOAD_FOLDER, filename))

            ruta_relativa = f'libros_pdf/{filename}'
                    # Crear y guardar el libro en la base de datos
            nuevo_libro = Book(
                titulo=new_titulo,
                autor=new_autor,
                anio_publicacion=new_anio,
                carrera=new_carrera,
                estado=new_estado,
                archivo_pdf=ruta_relativa,
            )
            db.session.add(nuevo_libro)
            db.session.commit()

            return jsonify({'mensaje': 'Libro subido correctamente'}), 201

        return jsonify({'error': 'Archivo no permitido'}), 400