from flask import Blueprint, request
from app.api.auth.access_control import roles_required

autor_bp = Blueprint('autores', __name__)


@autor_bp.route('/', methods=['POST'])
# @roles_required('usuario')
def agregar_autor_route():
    from app.api.autores.controllers import agregar_autor
    return agregar_autor()


@autor_bp.route("/", methods=["GET"])
# @roles_required('usuario')
def listar_autores_route():
    from app.api.autores.controllers import listar_autores
    return listar_autores()


@autor_bp.route("/<int:id_autor>", methods=["PUT"])
# @roles_required('usuario')
def actualizar_autor_route(id_autor):
    id_autor = str(id_autor)
    from app.api.autores.controllers import actualizar_autor
    return actualizar_autor(id_autor)


@autor_bp.route("/<int:id_autor>", methods=["DELETE"])
# @roles_required('usuario')
def eliminar_autor_route(id_autor):
    id_autor = str(id_autor)
    from app.api.autores.controllers import eliminar_autor
    return eliminar_autor(id_autor)
