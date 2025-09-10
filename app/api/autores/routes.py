from flask import Blueprint

autor_bp = Blueprint('autores', __name__)


@autor_bp.route('/', methods=['POST'])
def agregar_autor_route():
    from .controllers import agregar_autor
    return agregar_autor()


@autor_bp.route("/", methods=["GET"])
def listar_autores_route():
    from .controllers import listar_autores
    return listar_autores()


@autor_bp.route("/<int:id_autor>", methods=["PUT"])
def actualizar_autor_route(id_autor):
    from .controllers import actualizar_autor
    return actualizar_autor(id_autor)


@autor_bp.route("/<int:id_autor>", methods=["DELETE"])
def eliminar_autor_route(id_autor):
    from .controllers import eliminar_autor
    return eliminar_autor(id_autor)
