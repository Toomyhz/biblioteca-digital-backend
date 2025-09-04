from flask import request, jsonify
from app.api.carreras.services import agregar_carrera_service, actualizar_carrera_service, eliminar_carrera_service, leer_carreras_service

def agregar_carrera():
    if request.method == 'POST':
        data = request.form
        response, status = agregar_carrera_service(data)
        return jsonify(response), status
    else:
        return jsonify({'error': 'Método no permitido'}), 400

def actualizar_carrera(request):
    if request.method != 'PUT':
        return jsonify({'error': 'Método no permitido'}), 400

    data = request.get_json()
    id_carrera = data.get("id_carrera")
    if not id_carrera:
        return jsonify({'error': 'El ID de la carrera es obligatorio'}), 400
    
    carrera, mensaje, status = actualizar_carrera_service(id_carrera, data)
    
    if mensaje and status != 200:
        return jsonify({'error': mensaje}), 400 if status == 'El slug proporcionado ya existe para otra carrera' else 404
    
    return jsonify({
        'mensaje': 'Carrera actualizada correctamente', 
        'carrera': {
            'id_carrera': carrera.id_carrera,
            'nombre_carrera': carrera.nombre_carrera,
            'slug_carrera': carrera.slug_carrera
        }
    }), status
    
def eliminar_carrera(request):
    if request.method != 'DELETE':
        return jsonify({'error': 'Método no permitido'}), 400
    data = request.get_json()
    id_carrera = data.get("id_carrera")
    if not id_carrera:
        return jsonify({'error': 'El ID de la carrera es obligatorio'}), 400
    
    carrera, mensaje, status = eliminar_carrera_service(id_carrera)
    
    if mensaje and status != 200:
        return jsonify({'error': mensaje}), 404
    
    return jsonify({
            'mensaje': 'Carrera eliminada correctamente', 
            'carrera': {
                'id_carrera': carrera.id_carrera,
                'nombre_carrera': carrera.nombre_carrera,
                'slug_carrera': carrera.slug_carrera
            }
        }), status
    
def listar_carreras():
    if request.method != 'GET':
        return jsonify({'error': 'Método no permitido'}), 400
    
    carreras_list, status = leer_carreras_service()
    
    return jsonify(carreras_list), status