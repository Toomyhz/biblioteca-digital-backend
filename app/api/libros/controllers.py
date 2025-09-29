from flask import request, jsonify
from app.api.libros.services import agregar_libro_service, actualizar_libro_service, eliminar_libro_service, listar_libros_service


def agregar_libro():
    data = request.get_json()
    response, status = agregar_libro_service(data)
    return jsonify(response), status


def listar_libros():
    response, status = listar_libros_service()
    return jsonify(response), status


def actualizar_libro(id_libro):
    if not id_libro:
        return jsonify({'error': 'El ID del libro es obligatorio'}), 40

    data = request.get_json()
    response, status = actualizar_libro_service(id_libro, data)

    return jsonify(response), status


def eliminar_libro(id_libro):
    if not id_libro:
        return jsonify({'error': 'El ID del libro es obligatorio'}), 400
    response, status = eliminar_libro_service(id_libro)

    return jsonify(response), status
