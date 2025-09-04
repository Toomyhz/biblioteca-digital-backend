from app.models.autores import Autores
from app.api.utils.helpers import generar_slug
from app import db

def agregar_autor_service(data):
    nombre_completo = data.get("new_nombre")
    nacionalidad = data.get("new_nacionalidad")
    if not nombre_completo:
        return {'error': 'El nombre del autor es obligatorio'}, 400
    slug_autor = generar_slug(nombre_completo)
    
    nuevo_autor = Autores(
        nombre_completo=nombre_completo,
        nacionalidad=nacionalidad,
        slug_autor=slug_autor
    )
    
    db.session.add(nuevo_autor)
    db.session.commit()
    
    # Cambiar Slug con id
    id_autor = str(nuevo_autor.id_autor)
    slug_autor = generar_slug(nombre_completo, id_autor)
    nuevo_autor.slug_autor = slug_autor
    db.session.commit()

    return {'mensaje': 'Autor agregado correctamente', 'id': nuevo_autor.id_autor, 'slug': slug_autor}, 201

def actualizar_autor_service(id_autor, data):
    autor = Autores.query.get(id_autor)
    if not autor:
        return None, "Autor no encontrado", 404

    nombre_completo = data.get("edit_nombre")
    nacionalidad = data.get("edit_nacionalidad")
    slug_autor = generar_slug(nombre_completo, id_autor)
    
    if not nombre_completo:
        return None, "El nombre del autor es obligatorio", 400
    
    autor.nombre_completo = nombre_completo
    autor.nacionalidad = nacionalidad
    autor.slug_autor = slug_autor
    
    db.session.commit()
    
    return autor, {'mensaje': 'Autor actualizado correctamente', 'Nombre': autor.nombre_completo, 'slug': autor.slug_autor}, 200

def eliminar_autor_service(id_autor):
    autor = Autores.query.get(id_autor)
    if not autor:
        return {'error': 'Autor no encontrado'}, 404
    
    db.session.delete(autor)
    db.session.commit()
    
    return autor, {'mensaje': 'Autor eliminado correctamente'}, 200

def leer_autores_service():
    autores = Autores.query.order_by(Autores.id_autor.asc()).all()
    autores_list = [{
        'id_autor': autores.id_autor,
        'nombre_completo': autores.nombre_completo,
        'nacionalidad': autores.nacionalidad,
        'slug_autor': autores.slug_autor
    } for autores in autores]
    
    return autores_list, 200