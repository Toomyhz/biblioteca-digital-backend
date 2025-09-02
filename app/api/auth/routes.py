from flask import Blueprint, request, jsonify, redirect 
from .controllers import login_controller
import jwt
from app.config import Config
from app.api.auth.auth import token_required

ID_CLIENT='1069979014769-6rp1isa3hqb50188pbjhmrd0gm3093q0.apps.googleusercontent.com'
SECRET_CLIENT='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'

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/', methods=['GET'])
def login():
    return jsonify({"message": "Login successful"})

@auth_bp.route('/login/callback', methods=['POST'])
def callback():
    data = request.get_json()
    code = data.get('code')
    print(data)
    if code:
        return jsonify(code)
    else:
        return jsonify({'error': 'No authorization code provided'}), 400

@auth_bp.route('/validate', methods=['GET'])
def validate_token():
    print("Validando token..")
    access_token = request.cookies.get('access_token')
    if not access_token:
        return jsonify({'authenticated': False}), 401
    try:
        payload = jwt.decode(access_token, Config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'authenticated': True, 'user_id': payload['sub']}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'authenticated': False}), 401
    except jwt.InvalidTokenError:
        return jsonify({'authenticated': False}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logout successful"})
    response.delete_cookie('access_token')
    return response
