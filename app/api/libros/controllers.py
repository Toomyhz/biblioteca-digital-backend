from flask import request, jsonify
from app.api.libros.services import agregar_libro_service, actualizar_libro_service, eliminar_libro_service, leer_libros_service

def agregar_libro():
    if request.method != 'POST':
        return jsonify({'error': 'Método no permitido'}), 400
    
    data = request.form
    archivo = request.files.get('archivo-pdf')
    response, status= agregar_libro_service(data, archivo)
    return jsonify(response), status
    
def actualizar_libro(request):
    if request.method != 'PUT':
        return jsonify({'error': 'Método no permitido'}), 400
    
    data = request.form
    archivo = request.files.get("archivo-pdf")
    id_libro = data.get("id_libro")
    
    if not id_libro:
        return jsonify({'error': 'El ID del libro es obligatorio'}), 400

    response, status = actualizar_libro_service(id_libro, data, archivo)
    
    return jsonify(response), status

def eliminar_libro(request):
    if request.method != 'DELETE':
        return jsonify({'error': 'Método no permitido'}), 400

    data = request.form
    id_libro = data.get("id_libro")

    if not id_libro:
        return jsonify({'error': 'El ID del libro es obligatorio'}), 400

    response, status = eliminar_libro_service(id_libro)

    return jsonify(response), status

def listar_libros():
    if request.method != 'GET':
        return jsonify({'error': 'Método no permitido'}), 400
    
    response, status = leer_libros_service()
    
    return jsonify(response), status
    