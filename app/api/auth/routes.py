from flask import Blueprint, request,jsonify
from .controllers import login_controller
import jwt
from app.config import Config
from app.auth.auth import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    code = data.get('code')
    if code:
        return login_controller(code)
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
    