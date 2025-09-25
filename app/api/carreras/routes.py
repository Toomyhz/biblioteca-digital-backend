from flask import Blueprint, request

carrera_bp = Blueprint('carreras', __name__)


@carrera_bp.route('/', methods=['POST'])
def agregar_carrera_route():
    from .controllers import agregar_carrera
    return agregar_carrera()


@carrera_bp.route("/listar/", methods=['GET'])
def listar_carreras_route():
    from .controllers import listar_carreras
    return listar_carreras()


@carrera_bp.route("/<int:id_carrera>", methods=['PUT'])
def actualizar_carrera_route(id_carrera):
    from .controllers import actualizar_carrera
    return actualizar_carrera(id_carrera)


@carrera_bp.route("/<int:id_carrera>", methods=['DELETE'])
def eliminar_carrera_route(id_carrera):
    from .controllers import eliminar_carrera
    return eliminar_carrera(id_carrera)
