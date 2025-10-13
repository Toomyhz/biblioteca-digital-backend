from flask import request, jsonify
from app.api.libros.services import agregar_libro_service, actualizar_libro_service, eliminar_libro_service, listar_libros_service, listar_libros_home_service


def agregar_libro():
    data = request.form
    archivo = request.files
    response, status = agregar_libro_service(data, archivo)
    return jsonify(response), status

def listar_libros():
    response, status = listar_libros_service()
    return jsonify(response), status

def actualizar_libro(id_libro):
    data = request.form
    archivo = request.files
    response, status = actualizar_libro_service(id_libro, data, archivo)
    return jsonify(response), status

def eliminar_libro(id_libro):
    response, status = eliminar_libro_service(id_libro)
    return jsonify(response), status

def libros_home():
    response, status = listar_libros_home_service()
    return jsonify(response), status