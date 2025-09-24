from app import db
from app.models.asociaciones import libros_carreras

class Carreras(db.Model):
    __tablename__ = 'carreras'
    id_carrera = db.Column(
        db.Integer,
        db.Sequence("carreras_seq", start=1, increment=1),
        primary_key=True
        )
    nombre_carrera = db.Column(db.String(100), nullable=False)
    slug_carrera = db.Column(db.String(100), unique=True, nullable=False)
    
    libros = db.relationship(
        "Libros",
        secondary=libros_carreras,
        back_populates="carreras"
        )