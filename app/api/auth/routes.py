from flask import Blueprint, request, jsonify, redirect , session
from .controllers import login_controller
from app.api.auth.auth import token_required

from services import (
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

@auth_bp.route('/login/callback', methods=['POST'])
def callback():
    data = request.get_json()
    code = data.get('code')
    print(data)
    if code:
        return jsonify(code)
    else:
        return jsonify({'error': 'No authorization code provided'}), 400


@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logout successful"})
    response.delete_cookie('access_token')
    return response
