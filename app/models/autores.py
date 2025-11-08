from app.extensions import db
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

    def to_dict_basic(self):
        return {
            "id_autor": self.id_autor,
            "nombre_completo": self.nombre_completo,
            "nacionalidad": self.nacionalidad,
            "slug_autor": self.slug_autor,
        }

    # def to_dict(self, include_libros=True):
    #     data = {
    #         "id_autor": self.id_autor,
    #         "nombre_completo": self.nombre_completo,
    #         "nacionalidad": self.nacionalidad,
    #         "slug_autor": self.slug_autor,
    #     }
    #     if include_libros:
    #         data["libros"] = [libro.to_dict(
    #             include_autores=False) for libro in self.libros]
    #     return data
