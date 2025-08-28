from app import db
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    anio_publicacion = db.Column(db.Integer, nullable=True)
    carrera = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    archivo_pdf = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(DateTime(timezone=True), server_default=func.now())
 