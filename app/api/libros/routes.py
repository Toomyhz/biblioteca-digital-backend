from flask import Blueprint

libro_bp = Blueprint("libros", __name__)


@libro_bp.route("/", methods=['POST'])
def agregar_libro_route():
    from .controllers import agregar_libro
    return agregar_libro()


@libro_bp.route("/", methods=['GET'])
def listar_libro_route():
    from .controllers import listar_libros
    return listar_libros()


@libro_bp.route("/<int:id_libro>", methods=['PUT'])
def actualizar_libro_route(id_libro):
    id_libro = str(id_libro)
    from .controllers import actualizar_libro
    return actualizar_libro(id_libro)


@libro_bp.route("/<int:id_libro>", methods=['DELETE'])
def eliminar_libro_route(id_libro):
    id_libro = str(id_libro)
    from .controllers import eliminar_libro
    return eliminar_libro(id_libro)

# Endpoints para Home
@libro_bp.route("/home/",methods=["GET"])
def listar_libros_home():
    from .controllers import libros_home
    return libros_home()