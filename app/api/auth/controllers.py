from flask import jsonify,make_response
from app.models.usuarios import Usuarios
from app import db
from app.tokens.services import generar_access_token, generar_refresh_token
    

def crear_usuario(data):
    nuevo_usuario = Usuarios(
        email=data.get("email"),
        name=data.get("name"),
        picture=data.get("picture"),
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return nuevo_usuario
