from flask import Blueprint, request, jsonify, redirect , session, Response, send_file
from app.models.usuarios import Usuarios
from app.api.auth.access_control import roles_required
from app import db
import time
import json
from app.api.auth.helpers import oauth, oauth_ok

from flask_login import login_user, logout_user, current_user, login_required

from app.api.auth.services import (
    _build_google_auth_url,
    _exchange_code_for_tokens,
    _verify_id_token,
    _require_domain
)

import os

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
        return oauth(oauth_error)
    
    state = request.args.get("state")
    code = request.args.get("code")

    saved_state = session.get("oauth_state")
    saved_ts = session.get("oauth_state_ts", 0)

    # 2. Validar estado y tiempo de expiración
    now = int(time.time())
    if (not state) or (state != saved_state) or (now - int(saved_ts) > 300):
        return oauth("invalid_state")

    try:
        token_payload = _exchange_code_for_tokens(code)
        idt = token_payload.get("id_token")
        claims = _verify_id_token(idt)
    except Exception:
        return oauth("token_exchange_failed")
    
    # 3. Validar nonce
    nonce = session.get("oauth_nonce")
    if (not claims) or claims.get("nonce") != nonce:
        return oauth("invalid_nonce")
    # 4. Validar email  y dominio
    email = claims.get("email")
    email_verified = claims.get("email_verified")
    if not email or not email_verified:
        return oauth("email_unverified")

    if not _require_domain(email):
        return oauth("invalid_domain")

    # 5. Limpieza artefactos OAuth
    session.pop("oauth_state", None)
    session.pop("oauth_state_ts", None)
    session.pop("oauth_nonce", None)

    # 6. Upsert de usuario en BD
    user = Usuarios.query.filter_by(correo_institucional=email).first()
    if not user:
        # Crear nuevo usuario
        user = Usuarios(
            correo_institucional=claims.get("email"),
            nombre_usuario=claims.get("name"),
            foto_perfil=claims.get("picture"),
            rol="usuario"  # Rol por defecto
        )
        print("Nuevo usuario creado:", user)
        db.session.add(user)
    else:
        # Actualizar datos existentes
        user.nombre_usuario = claims.get("name")
        user.foto_perfil = claims.get("picture")

    db.session.commit()
    # 7. LOG IN del usuario (crear sesión)
    login_user(user,remember=False)

    return oauth_ok()

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

@auth_bp.route('/libro/test/', methods=['GET'])
def get_page():
    ruta = r"api\auth\libros\LLL.pdf"
    rango = request.headers.get('Range', None)

    if not rango:  # descarga completa si no hay Range
        return send_file(ruta, mimetype="application/pdf")

    size = os.path.getsize(ruta)
    start, end = rango.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else size - 1

    with open(ruta, "rb") as f:
        f.seek(start)
        data = f.read(end - start + 1)

    resp = Response(data, 206, mimetype="application/pdf")
    resp.headers.add("Content-Range", f"bytes {start}-{end}/{size}")
    resp.headers.add("Accept-Ranges", "bytes")
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp