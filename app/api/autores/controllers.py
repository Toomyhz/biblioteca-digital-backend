from flask import request, jsonify
from app.api.autores.services import agregar_autor_service, actualizar_autor_service, eliminar_autor_service, leer_autores_service

def agregar_autor():
    if request.method == 'POST':
        data = request.form
        response, status = agregar_autor_service(data)
        return jsonify(response), status
    else:
        return jsonify({'error': 'Método no permitido'}), 400
    
def actualizar_autor(request):
    if request.method != 'PUT':
        return jsonify({'error': 'Método no permitido'}), 400

    data = request.get_json()
    id_autor = data.get("id_autor")
    if not id_autor:
        return jsonify({'error': 'El ID del autor es obligatorio'}), 400
    
    autor, mensaje, status = actualizar_autor_service(id_autor, data)
    
    if mensaje and status != 200:
        return jsonify({'error': mensaje}), 400 if status == 'El slug proporcionado ya existe para otro autor' else 404
    
    return jsonify({
        'mensaje': 'Autor actualizado correctamente', 
        'autor': {
            'id_autor': autor.id_autor,
            'nombre_completo': autor.nombre_completo,
            'nacionalidad': autor.nacionalidad,
            'slug_autor': autor.slug_autor
        }
    }), status

def eliminar_autor(request):
    if request.method != 'DELETE':
        return jsonify({'error': 'Método no permitido'}), 400
    data = request.get_json()
    id_autor = data.get("id_autor")
    if not id_autor:
        return jsonify({'error': 'El ID del autor es obligatorio'}), 400
    
    autor, mensaje, status = eliminar_autor_service(id_autor)
    
    if mensaje and status != 200:
        return jsonify({'error': mensaje}), 404
    
    return jsonify({
            'mensaje': 'Autor eliminado correctamente', 
            'autor': {
                'id_autor': autor.id_autor,
                'nombre_completo': autor.nombre_completo,
                'nacionalidad': autor.nacionalidad,
                'slug_autor': autor.slug_autor
            }
        }), status
    
def listar_autores():
    if request.method != 'GET':
        return jsonify({'error': 'Método no permitido'}), 400
    
    autores_list, status = leer_autores_service()
    
    return jsonify(autores_list), status