import jwt
import datetime
from app.config import Config
def generar_access_token(user):
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
            'sub': user.id,
            'google_id': user.google_id,
            'iat': utc_now,
            'exp': utc_now + datetime.timedelta(hours=1)
        }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token

def generar_refresh_token(user):
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
            'sub': user.id,
            'google_id': user.google_id,
            'iat': utc_now,
            'exp': utc_now + datetime.timedelta(days=30)
        }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token