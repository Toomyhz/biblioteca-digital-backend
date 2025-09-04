from app import db
from flask_login import UserMixin

from sqlalchemy import Integer, String, Sequence
class Usuarios(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, Sequence('usuario_id_seq'), primary_key=True)
    nombre_usuario = db.Column(db.String(255), nullable=False)
    correo_institucional = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    foto_perfil = db.Column(db.String(255), nullable=True)

