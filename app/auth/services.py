import requests
from app.config import Config
def obtener_token(code):
    data = {
        'code':code,
        'client_id': Config.GOOGLE_CLIENT_ID,
        'client_secret': Config.GOOGLE_CLIENT_SECRET,
        'redirect_uri': Config.REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.post(Config.TOKEN_URL, data=data)
        response_data = response.json()

        if response.status_code != 200 or 'access_token' not in response_data:
            return {'error': 'No se pudo obtener el token de acceso'}, 400
        
        access_token = response_data['access_token']
        return access_token, None
    except requests.exceptions.RequestException as e:
        return None, {'error': str(e)}
    
def obtener_informacion_usuario(access_token):
    user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    try:
        user_info_response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})  
        user_info = user_info_response.json()

        if user_info_response.status_code != 200:
            return None, {'error': 'No se pudo obtener la información del usuario'}

        return user_info, None
    except requests.exceptions.RequestException as e:
        return None, {'error': str(e)}  