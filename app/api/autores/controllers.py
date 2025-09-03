from flask import request, jsonify
from app.api.autores.services import agregar_autor_service

def agregar_autor():
    if request.method == 'POST':
        data = request.form
        response, status = agregar_autor_service(data)
        return jsonify(response), status
    else:
        return jsonify({'error': 'Método no permitido'}), 400
    
