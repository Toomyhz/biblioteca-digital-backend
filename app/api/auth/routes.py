from flask import Blueprint, request, jsonify, redirect , session
from app.api.auth.auth import token_required
import time

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

    data_form = {
        'email': claims.get("email"),
        'name': claims.get("name"),
        'picture': claims.get("picture"),
    }

    session.pop("oauth_state", None)
    session.pop("oauth_nonce", None)

    # Aquí puedes guardar el usuario en la base de datos

    return jsonify({"message": "Login successful", "data": data_form})

