from flask import Blueprint, request

libro_bp = Blueprint("libros", __name__)

@libro_bp.route("/agregar/", methods=['POST'])
def agregar_libro_route():
    from .controllers import agregar_libro
    return agregar_libro()

@libro_bp.route("/actualizar/", methods=['PUT'])
def actualizar_libro_route():
    from .controllers import actualizar_libro
    return actualizar_libro(request)

@libro_bp.route("/eliminar/", methods=['DELETE'])
def eliminar_libro_route():
    from .controllers import eliminar_libro
    return eliminar_libro(request)

@libro_bp.route("/listar/", methods=['GET'])
def listar_libro_route():
    from .controllers import listar_libros
    return listar_libros()