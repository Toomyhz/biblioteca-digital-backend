from flask import Blueprint, request, jsonify

token_bp = Blueprint('tokens', __name__)
@token_bp.route('/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'No refresh token provided'}), 400
    
    # Aquí deberías verificar el refresh token y generar un nuevo access token
    # Por simplicidad, este ejemplo solo devuelve un nuevo access token ficticio
    new_access_token = "nuevo_access_token_ficticio"
    
    return jsonify({'access_token': new_access_token}), 200