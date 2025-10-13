from flask import Blueprint

biblioteca_bp = Blueprint("biblioteca", __name__)


@biblioteca_bp.route("/", methods=['GET'])
def get_biblioteca():
    from .controllers import listado_biblioteca
    return listado_biblioteca()

