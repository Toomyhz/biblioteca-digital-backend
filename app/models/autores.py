from app import db
from app.models.asociaciones import libros_autores

class Autores(db.Model):
    __tablename__ = 'autores'
    
    id_autor = db.Column(
    db.Integer,
    db.Sequence("autores_seq", start=1, increment=1),
    primary_key=True
    )
    nombre_completo = db.Column(db.String(100), nullable=False)
    nacionalidad = db.Column(db.String(255), nullable=True)
    slug_autor = db.Column(db.String(255), unique=True, nullable=False)
    
    libros = db.relationship(
        "Libros",
        secondary=libros_autores,
        back_populates="autores"
    )
    
    