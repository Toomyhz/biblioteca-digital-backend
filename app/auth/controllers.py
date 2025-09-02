from flask import jsonify,make_response
from .services import obtener_token, obtener_informacion_usuario
from app.models.usuarios import Usuarios as User
from app import db
from app.tokens.services import generar_access_token, generar_refresh_token


def login_controller(code):

    # Obtener el token de acceso utilizando el código de autorización
    access_token, error = obtener_token(code)
    if error:
        return jsonify(error), 400
    
    # Obtener la información del usuario utilizando el token de acceso
    user_info, error = obtener_informacion_usuario(access_token)
    if error:
        return jsonify(error), 400
    
    # Validar correo permitido
    # if not user_info['email'].endswith('@umce.cl'):
    #     return jsonify({'error': 'Correo no permitido'}), 403

    existing_user = User.query.filter_by(google_id=user_info['id']).first()

    if existing_user:
        access_token = generar_access_token(existing_user)
        refresh_token = generar_refresh_token(existing_user)
        return jsonify({'message': 'Usuario ya existe', 'access_token':access_token, 'refresh_token':refresh_token}), 200
    
    # Crear un nuevo usuario si no existe
    new_user = User(
         google_id = user_info['id'],
         email = user_info['email'],
         nombre = user_info.get('name', 'Sin nombre'),
         id_rol = 1
    ) 

    db.session.add(new_user)
    db.session.commit()

    access_token = generar_access_token(new_user)
    refresh_token = generar_refresh_token(new_user)
    resp = make_response(jsonify({'message': 'Login exitoso'}))
    # Cambiar secure a True si se usa HTTPS
    resp.set_cookie('access_token', access_token, httponly=False, secure=False, samesite='Lax')
    resp.set_cookie('refresh_token', refresh_token, httponly=False, secure=False, samesite='Lax')
    return resp, 200
    



    