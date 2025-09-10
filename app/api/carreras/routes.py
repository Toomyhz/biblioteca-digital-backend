from flask import Blueprint, request

carrera_bp = Blueprint('carreras', __name__)

@carrera_bp.route('/agregar/', methods=['POST'])
def agregar_carrera_route():
    from .controllers import agregar_carrera
    return agregar_carrera()

@carrera_bp.route("/actualizar/", methods=["PUT"])
def actualizar_carrera_route():
    from .controllers import actualizar_carrera
    return actualizar_carrera(request)

@carrera_bp.route("/eliminar/", methods=["DELETE"])
def eliminar_carrera_route():
    from .controllers import eliminar_carrera
    return eliminar_carrera(request)

@carrera_bp.route("/listar/", methods=["GET"])
def listar_carreras_route():
    from .controllers import listar_carreras
    return listar_carreras()