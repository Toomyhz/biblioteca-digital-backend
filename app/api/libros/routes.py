from flask import Blueprint, request

libro_bp = Blueprint("libros", __name__)

@libro_bp.route("/agregar/", methods=['POST'])
def agregar_libro_route():
    from .controllers import agregar_libro
    return agregar_libro()

@libro_bp.route("/actualizar/", methods=['PUT'])
def actualizar_autor_route():
    from .controllers import actualizar_libro
    return actualizar_libro(request)


