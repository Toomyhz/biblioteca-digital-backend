from flask import Blueprint, request

autor_bp = Blueprint('autores', __name__)

@autor_bp.route('/agregar/', methods=['POST'])
def agregar_autor_route():
    from app.api.autores.controllers import agregar_autor
    return agregar_autor()

@autor_bp.route("/actualizar/", methods=["PUT"])
def actualizar_autor_route():
    from app.api.autores.controllers import actualizar_autor
    return actualizar_autor(request)

@autor_bp.route("/eliminar/", methods=["DELETE"])
def eliminar_autor_route():
    from app.api.autores.controllers import eliminar_autor
    return eliminar_autor(request)

@autor_bp.route("/listar/", methods=["GET"])
def listar_autores_route():
    from app.api.autores.controllers import listar_autores
    return listar_autores()