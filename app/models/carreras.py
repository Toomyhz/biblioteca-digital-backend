from app import db

class Carreras(db.Model):
    __tablename__ = 'carreras'
    id_carrera = db.Column(db.Integer, primary_key=True)
    nombre_carrera = db.Column(db.String(100), nullable=False)
    slug_carrera = db.Column(db.String(100), unique=True, nullable=False)