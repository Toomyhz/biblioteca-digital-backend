from app import db

libros_autores = db.Table(
    'libros_autores',
    db.Column('libro_id', db.Integer, db.ForeignKey('libros.id'), primary_key=True),
    db.Column('autor_id', db.Integer, db.ForeignKey('autores.id'), primary_key=True)
)