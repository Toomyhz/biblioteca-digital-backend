from app.api.utils.helpers import generar_slug
from app import db
from flask import jsonify

def agregar_autor_service(data):
    nombre = data.get("nombre")
    if not nombre:
        return jsonify({'error': 'El nombre del autor es obligatorio'}), 400
    slug = generar_slug(nombre)
    
    nuevo_autor = Autores(
        nombre=nombre,
        nacionalidad=data.get("nacionalidad"),
        slug=slug
    )
    db.session.add(nuevo_autor)
    db.session.commit()
    return jsonify({'mensaje': 'Autor agregado correctamente', 'id': nuevo_autor.id, 'slug': slug}), 201