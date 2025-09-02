from flask import Blueprint, request, jsonify, redirect , session
from app.api.auth.auth import token_required

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
    data = request.args
    return jsonify({"message": "Callback endpoint", "data": data})

