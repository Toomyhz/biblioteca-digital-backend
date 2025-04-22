import requests
from flask import jsonify
id_cliente = "1069979014769-6rp1isa3hqb50188pbjhmrd0gm3093q0.apps.googleusercontent.com"
secreto_cliente = "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"
redirect_uri = "http://localhost:5173/login/callback"

token_url = 'https://oauth2.googleapis.com/token'
def login_controller(code):
    data = {
        'code': code,
        'client_id': id_cliente,
        'client_secret': secreto_cliente,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    try:
        response = requests.post(token_url, data=data)
        response_data = response.json()

        if response.status_code != 200 or 'access_token' not in response_data:
            return {'error': 'Failed to obtain access token'}, 400
        
        access_token = response_data['access_token']
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        user_info_response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
        user_info = user_info_response.json()

        if user_info_response.status_code != 200:
            return {'error': 'Failed to obtain user info'}, 400
        
        if user_info['hd'] not in ['duocuc.cl']:
            return {'error': 'El correo no pertenece a la institución'}, 400
        
        return jsonify({'message': 'Autenticación exitosa', 'user_info': user_info})
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500
    