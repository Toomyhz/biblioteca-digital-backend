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
    def __str__(self):
        return super().__str__() + f" - {self.titulo}"
 