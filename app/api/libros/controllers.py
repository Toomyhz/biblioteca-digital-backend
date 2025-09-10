from flask import request, jsonify
from app.api.libros.services import agregar_libro_service, actualizar_libro_service

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