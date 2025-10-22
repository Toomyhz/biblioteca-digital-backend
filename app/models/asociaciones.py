from app.extensions import db

libros_autores = db.Table(
    "libros_autores",
    db.Column("id_libro", db.Integer, db.ForeignKey("libros.id_libro", ondelete="CASCADE"), primary_key=True),
    db.Column("id_autor", db.Integer, db.ForeignKey("autores.id_autor", ondelete="CASCADE"), primary_key=True)
)

libros_carreras = db.Table(
    "libros_carreras",
    db.Column("id_libro", db.Integer, db.ForeignKey("libros.id_libro", ondelete="CASCADE"), primary_key=True),
    db.Column("id_carrera", db.Integer, db.ForeignKey("carreras.id_carrera", ondelete="CASCADE"), primary_key=True)
)