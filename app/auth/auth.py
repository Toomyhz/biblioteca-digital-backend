from flask import request, jsonify
import jwt
from functools import wraps
from app.config import Config
# Decorador para validar el token de acceso
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.cookies.get('access_token')  # Obtener el token de las cookies

        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401

        try:
            # Intentar decodificar el token
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'El token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

        return f(payload, *args, **kwargs)  # Pasar la carga útil del token a la vista

    return decorator
