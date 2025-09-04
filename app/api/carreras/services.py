from app.models.carreras import Carreras
from app.api.utils.helpers import generar_slug 
from app import db

def agregar_carrera_service(data):
    nombre_carrera = data.get("new_nombre")
    if not nombre_carrera:
        return {'error': 'El nombre de la carrera es obligatorio'}, 400
    slug_carrera = generar_slug(nombre_carrera)
    
    nueva_carrera = Carreras(
        nombre_carrera=nombre_carrera,
        slug_carrera=slug_carrera
    )
    
    db.session.add(nueva_carrera)
    db.session.commit()
    
    # Cambiar Slug con id
    id_carrera = str(nueva_carrera.id_carrera)
    slug_carrera = generar_slug(nombre_carrera, id_carrera)
    nueva_carrera.slug_carrera = slug_carrera
    db.session.commit()
    
    return {'mensaje': 'Carrera agregada correctamente', 
            'id': nueva_carrera.id_carrera,
            'nombre': nombre_carrera,
            'slug': slug_carrera}, 201

def actualizar_carrera_service(id_carrera, data):
    carrera = Carreras.query.get(id_carrera)
    if not carrera:
        return None, "Carrera no encontrada", 404

    nombre_carrera = data.get("edit_nombre")
    slug_carrera = generar_slug(nombre_carrera, id_carrera)
    
    if not nombre_carrera:
        return None, "El nombre de la carrera es obligatorio", 400
    
    carrera.nombre_carrera = nombre_carrera
    carrera.slug_carrera = slug_carrera
    
    db.session.commit()
    
    return carrera, {'mensaje': 'Carrera actualizada correctamente', 'Nombre': carrera.nombre_carrera, 'slug': carrera.slug_carrera}, 200

def eliminar_carrera_service(id_carrera):
    carrera = Carreras.query.get(id_carrera)
    if not carrera:
        return {'error': 'Carrera no encontrada'}, 404
    
    db.session.delete(carrera)
    db.session.commit()
    
    return carrera, {'mensaje': 'Carrera eliminada correctamente'}, 200

def leer_carreras_service():
    carreras = Carreras.query.order_by(Carreras.id_carrera.asc()).all()
    carreras_list = [{
        'id_carrera': carrera.id_carrera,
        'nombre_carrera': carrera.nombre_carrera,
        'slug_carrera': carrera.slug_carrera
    } for carrera in carreras]
    
    return carreras_list, 200