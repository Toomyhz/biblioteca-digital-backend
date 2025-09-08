from flask import request, jsonify
from app.api.libros.services import agregar_libro_service

def agregar_libro():
    if request.method == 'POST':
        data = request.form
        archivo = request.files.get('archivo-pdf')
        response = agregar_libro_service(data, archivo)
        return response
    else:
        return jsonify({'error': 'Archivo no permitido'}), 400
    
def mostrar_libro():
    return "Mostrar libro"

def mostrar_libro():
    pass