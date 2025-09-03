from flask import Blueprint
from app.api.autores.controllers import agregar_autor

autor_bp = Blueprint('autores', __name__)

autor_bp.route('/agregar/', methods=['POST'])(agregar_autor)