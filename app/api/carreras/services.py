from app.models.carreras import Carreras
from app.api.utils.helpers import generar_slug
from app import db


def agregar_carrera_service(data):
    try:
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

        return {
            'mensaje': 'Carrera agregada correctamente',
            'carrera': nueva_carrera.to_dict_basic()
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al crear carrera: {e}'}, 500


def leer_carreras_service():
    try:
        carreras = Carreras.query.order_by(Carreras.id_carrera.asc()).all()
        carreras_dict = [carrera.to_dict() for carrera in carreras]
        return carreras_dict, 200
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al leer carreras: {e}'}, 500


def actualizar_carrera_service(id_carrera, data):
    try:
        carrera = Carreras.query.get(id_carrera)
        if not carrera:
            return None, "Carrera no encontrada", 404

        nombre_carrera = data.get("edit_nombre")
        slug_carrera = generar_slug(nombre_carrera, str(id_carrera))

        if not nombre_carrera:
            return None, "El nombre de la carrera es obligatorio", 400

        carrera.nombre_carrera = nombre_carrera
        carrera.slug_carrera = slug_carrera

        db.session.commit()

        return {'mensaje': 'Carrera actualizada correctamente',
                'carrera': carrera.to_dict_basic()
                }, 200
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al actualizar carrera: {e}'}, 500


def eliminar_carrera_service(id_carrera):
    try:
        carrera = Carreras.query.get(id_carrera)
        if not carrera:
            return {'error': 'Carrera no encontrada'}, 404

        db.session.delete(carrera)
        db.session.commit()

        return {'mensaje': 'Carrera eliminada correctamente',
                'carrera': carrera.to_dict()
                }, 200
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al eliminar carrera: {e}'}, 500
