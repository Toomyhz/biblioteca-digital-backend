from app.extensions import db
from app.models.asociaciones import libros_autores, libros_carreras
from datetime import datetime, timezone

class Libros(db.Model):
    __tablename__ = 'libros'

    id_libro = db.Column(db.Integer,
                         db.Sequence("libros_seq", start=1, increment=1),
                         primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(50), nullable=True)
    anio_publicacion = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(50), default='disponible')
    archivo_pdf = db.Column(db.String(255), nullable=True)
    archivo_portada = db.Column(db.String(255), nullable=True)
    slug_titulo = db.Column(db.String(300), unique=True, nullable=False)
    visualizaciones = db.Column(db.Integer, default=0, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now(timezone.utc))

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

    def to_dict_basic(self):
        return {
            "id_libro": self.id_libro,
            "titulo": self.titulo,
            "isbn": self.isbn,
            "anio_publicacion": self.anio_publicacion,
            "estado": self.estado,
            "archivo_pdf": self.archivo_pdf,
            "archivo_portada": self.archivo_portada,
            "slug_titulo": self.slug_titulo,
            "visualizaciones": self.visualizaciones,
        }

    def to_dict(self, include_autores=True, include_carreras=True):
        data = {
            "id_libro": self.id_libro,
            "titulo": self.titulo,
            "isbn": self.isbn,
            "anio_publicacion": self.anio_publicacion,
            "estado": self.estado,
            "archivo_pdf": self.archivo_pdf,
            "archivo_portada": self.archivo_portada,
            "slug_titulo": self.slug_titulo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "visualizaciones": self.visualizaciones,
        }
        if include_autores:
            data["autores"] = [autor.to_dict_basic() for autor in self.autores]
        if include_carreras:
            data["carreras"] = [carrera.to_dict_basic()
                                for carrera in self.carreras]
        return data

    def incrementar_clicks(self):
        """Incrementa el contador de clicks en 1"""
        self.visualizaciones += 1
        db.session.commit()