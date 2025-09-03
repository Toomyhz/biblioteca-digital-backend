from app.models.autores import Autores
from app.api.utils.helpers import generar_slug
from app import db

def agregar_autor_service(data):
    nombre_completo = data.get("new_nombre")
    if not nombre_completo:
        return {'error': 'El nombre del autor es obligatorio'}, 400
    slug_autor = generar_slug(nombre_completo)
    
    nuevo_autor = Autores(
        nombre_completo=nombre_completo,
        nacionalidad=data.get("new_nacionalidad"),
        slug_autor=slug_autor
    )
    db.session.add(nuevo_autor)
    db.session.commit()
    return {'mensaje': 'Autor agregado correctamente', 'id': nuevo_autor.id_autor, 'slug': slug_autor}, 201