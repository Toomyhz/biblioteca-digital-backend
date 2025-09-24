from flask import Blueprint, request
from app.api.auth.access_control import roles_required

autor_bp = Blueprint('autores', __name__)

@autor_bp.route('/agregar/', methods=['POST'])
@roles_required('admin')
def agregar_autor_route():
    from app.api.autores.controllers import agregar_autor
    return agregar_autor()

@autor_bp.route("/actualizar/", methods=["PUT"])
@roles_required('admin')    
def actualizar_autor_route():
    from app.api.autores.controllers import actualizar_autor
    return actualizar_autor(request)

@autor_bp.route("/eliminar/", methods=["DELETE"])
@roles_required('admin')
def eliminar_autor_route():
    from app.api.autores.controllers import eliminar_autor
    return eliminar_autor(request)

@autor_bp.route("/listar/", methods=["GET"])
@roles_required('admin')
def listar_autores_route():
    from app.api.autores.controllers import listar_autores
    return listar_autores()