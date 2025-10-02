from flask import (Blueprint, 
                   request, 
                   jsonify, 
                   redirect, 
                   session)
from app.api.auth.helpers import oauth, oauth_ok
from .controllers import manejar_callback

from flask_login import (
    logout_user, 
    current_user, 
    login_required)

from app.api.auth.services import (
    _build_google_auth_url,
)


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/', methods=['GET'])
def login():
    return redirect(_build_google_auth_url())


@auth_bp.route('/callback/', methods=['GET'])
def callback():
    # 1. Errores del proveedor
    error = request.args.get("error")
    if error:
        return oauth(error)
    return manejar_callback(request)
    

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route('/me', methods=['GET'])
@auth_bp.route('/me/', methods=['GET'])
def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({"is_authenticated": False, "user": None}), 200

    return jsonify({
            "is_authenticated": True,
            "user": {
                "id": current_user.id_usuario,
                "correo_institucional": current_user.correo_institucional,
                "nombre_usuario": current_user.nombre_usuario,
                "foto_perfil": current_user.foto_perfil,
                "rol": current_user.rol
            }
        }), 200

@auth_bp.route('/me/admin', methods=['GET'])
def is_admin():
    return jsonify({
        "is_authenticated": current_user.is_authenticated,
        "is_admin": current_user.is_authenticated and current_user.rol == "admin"
    }), 200