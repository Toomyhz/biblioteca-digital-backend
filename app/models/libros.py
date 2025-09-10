from app import db
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime
from app.models.asociaciones import libros_autores, libros_carreras
from sqlalchemy import Sequence

class Libros(db.Model):
    __tablename__ = 'libros'

    id_libro = db.Column(db.Integer,
                         db.Sequence("libros_seq", start= 1, increment=1),
                         primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(100), nullable=True)
    anio_publicacion = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(50), nullable=False)
    archivo_pdf = db.Column(db.String(200), nullable=False)
    slug_titulo = db.Column(db.String(255), unique=True, nullable=False)
    
    autores = db.relationship(
        "Autores",
        secondary=libros_autores,
        back_populates="libros"
    )
    carreras = db.relationship(
        "Carreras",
        secondary=libros_carreras,
        back_populates="libros"
    )
    def to_dict(self, include_autores=True, include_carreras=True):
        data = {
            "id_libro": self.id_libro,
            "titulo": self.titulo,
            "isbn": self.isbn,
            "anio_publicacion": self.anio_publicacion,
            "estado": self.estado,
            "archivo_pdf": self.archivo_pdf,
            "slug_titulo": self.slug_titulo,
        }
        if include_autores:
            data["autores"] = [autor.to_dict(include_libros=False) for autor in self.autores]
        if include_carreras:
            data["carreras"] = [carrera.to_dict(include_libros=False) for carrera in self.carreras]
        return data
 