from app import db
from app.models.asosiaciones import libros_autores

class Autores(db.Model):
    __tablename__ = 'autores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nacionalidad = db.Column(db.String(100), nullable=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    
    libros = db.relationship(
        "Libro",
        secondary=libros_autores,
        back_populates="autores"
    )
    
    