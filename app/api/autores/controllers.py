from flask import request, jsonify
from app.api.autores.services import agregar_autor_service, actualizar_autor_service, eliminar_autor_service, listar_autores_service


def agregar_autor():
    data = request.form
    response, status = agregar_autor_service(data)
    return jsonify(response), status


def listar_autores():
    response, status = listar_autores_service()
    return jsonify(response), status


def actualizar_autor(id_autor):
    data = request.get_json()
    response, status = actualizar_autor_service(id_autor, data)

    if not id_autor:
        return jsonify({'error': 'El ID del autor es obligatorio'}), 400
    elif status != 200:
        return jsonify({'error': response}), status

    return jsonify(response), status


def eliminar_autor(id_autor):
    response, status = eliminar_autor_service(id_autor)

    if not id_autor:
        return jsonify({'error': 'El ID del autor es obligatorio'}), 400
    elif status != 200:
        return jsonify({'error': response}), status

    return jsonify(response), status
