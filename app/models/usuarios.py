from app import db

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

