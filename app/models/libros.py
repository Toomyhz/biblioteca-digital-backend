from app import db
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime
from app.models.asociaciones import libros_autores
from sqlalchemy import Sequence

class Libro(db.Model):
    __tablename__ = 'libros'

    id_libro = db.Column(db.Integer, Sequence('userd_id_seq'), primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(100), nullable=False)
    anio_publicacion = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(50), nullable=False)
    archivo_pdf = db.Column(db.String(200), nullable=False)
    slug_titulo = db.Column(db.String(255), unique=True, nullable=False)
    autores = db.relationship(
        "Autores",
        secondary=libros_autores,
        back_populates="libros"
    )
 