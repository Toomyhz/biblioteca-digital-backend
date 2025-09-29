from flask import request, jsonify
from app.api.carreras.services import agregar_carrera_service, actualizar_carrera_service, eliminar_carrera_service, leer_carreras_service


def agregar_carrera():
    data = request.get_json()
    response, status = agregar_carrera_service(data)
    return jsonify(response), status


def listar_carreras():
    response, status = leer_carreras_service()
    return jsonify(response), status


def actualizar_carrera(id_carrera):
    data = request.get_json()
    response, status = actualizar_carrera_service(id_carrera, data)

    if not id_carrera:
        return jsonify({'error': 'El ID de la carrera es obligatorio'}), 400
    elif status != 200:
        return jsonify({'error': response}), status

    return jsonify(response), status


def eliminar_carrera(id_carrera):
    response, status = eliminar_carrera_service(id_carrera)

    if not id_carrera:
        return jsonify({'error': 'El ID de la carrera es obligatorio'}), 400
    elif status != 200:
        return jsonify({'error': response}), status

    return jsonify(response), status
