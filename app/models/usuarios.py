from app import db
from sqlalchemy import Integer, String, Sequence
class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, Sequence('usuario_id_seq'), primary_key=True)
    nombre_usuario = db.Column(db.String(255), nullable=False)
    correo_institucional = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False)

