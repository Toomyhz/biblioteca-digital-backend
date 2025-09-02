from flask import Blueprint
from .controllers import agregar_libro

libro_bp = Blueprint('libros', __name__)
libro_bp.route('/agregar/', methods=['GET'])(agregar_libro)