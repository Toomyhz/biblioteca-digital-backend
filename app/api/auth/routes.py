from flask import Blueprint, request, jsonify, redirect , session
from app.api.auth.auth import token_required
from app.models.usuarios import Usuarios
from app import db
import time

from flask_login import login_user, logout_user, current_user, login_required

from app.api.auth.services import (
    _build_google_auth_url,
    _exchange_code_for_tokens,
    _verify_id_token,
    _require_domain
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/', methods=['GET'])
def login():
    # Limpiar estados antiguos
    session.pop("user_id", None)
    return redirect(_build_google_auth_url())


@auth_bp.route('/callback/', methods=['GET'])
def callback():
    # 1. Manejar errores del proveedor
    oauth_error = request.args.get("error")
    if oauth_error:
        return jsonify({"message": f"Error from provider: {oauth_error}"}), 400
    
    state = request.args.get("state")
    code = request.args.get("code")

    saved_state = session.get("oauth_state")
    saved_ts = session.get("oauth_state_ts", 0)

    # 2. Validar estado y tiempo de expiración
    now = int(time.time())
    if (not state) or (state != saved_state) or (now - int(saved_ts) > 300):
        return jsonify({"message": "Error from provider: Invalid state"}), 400

    try:
        token_payload = _exchange_code_for_tokens(code)
        idt = token_payload.get("id_token")
        claims = _verify_id_token(idt)
    except Exception as e:
        return jsonify({"message": f"Error from provider: {str(e)}"}), 400

    # 3. Validar nonce
    nonce = session.get("oauth_nonce")
    if (not claims) or claims.get("nonce") != nonce:
        return jsonify({"message": "Error from provider: Invalid nonce"}), 400

    # 4. Validar email  y dominio
    email = claims.get("email")
    email_verified = claims.get("email_verified")
    if not email or not email_verified:
        return jsonify({"message": "Error from provider: Email not verified"}), 400

    if not _require_domain(email):
        return jsonify({"message": "Error from provider: Invalid domain"}), 400
    
    # 5. Limpieza artefactos OAuth
    session.pop("oauth_state", None)
    session.pop("oauth_state_ts", None)
    session.pop("oauth_nonce", None)

    # 6. Upsert de usuario en BD
    user = Usuarios.query.filter_by(email=email).first()
    if not user:
        # Crear nuevo usuario
        user = Usuarios(
            correo_institucional=claims.get("email"),
            nombre_usuario=claims.get("name"),
            foto_perfil=claims.get("picture"),
            rol="usuario"  # Rol por defecto
        )
        db.session.add(user)
    else:
        # Actualizar datos existentes
        user.nombre_usuario = claims.get("name")
        user.foto_perfil = claims.get("picture")

    db.session.commit()
    # 7. LOG IN del usuario (crear sesión)
    login_user(user,remember=False)
    session["_fresh_login"] = user.id_usuario

    return jsonify({"message": "Login successful", "data": {"correo_institucional": user.correo_institucional, "nombre_usuario": user.nombre_usuario, "foto_perfil": user.foto_perfil}}), 200

