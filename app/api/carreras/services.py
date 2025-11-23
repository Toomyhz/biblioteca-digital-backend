from app.models.carreras import Carreras
from app.api.utils.helpers import generar_slug
from app import db
from .errors import ValidationError, NotFoundError, ServiceError


def agregar_carrera_service(data):
    nombre_carrera = data.get("new_nombre_carrera")
    if not nombre_carrera:
        raise ValidationError("El nombre de la carrera es obligatorio")

    try:
        slug_carrera = generar_slug(nombre_carrera)
        nueva_carrera = Carreras(
            nombre_carrera=nombre_carrera,
            slug_carrera=slug_carrera
        )

        db.session.add(nueva_carrera)
        db.session.commit()

        # Actualiza slug con el ID real
        slug_carrera = generar_slug(
            nombre_carrera, str(nueva_carrera.id_carrera))
        nueva_carrera.slug_carrera = slug_carrera
        db.session.commit()

        return nueva_carrera.to_dict_basic()

    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Error al crear carrera: {e}")


def listar_carreras_service():
        carreras = Carreras.query.order_by(Carreras.id_carrera.asc()).all()
        return [carrera.to_dict_basic() for carrera in carreras]

def actualizar_carrera_service(id_carrera, data):
    carrera = Carreras.query.get(id_carrera)
    if not carrera:
        raise NotFoundError("Carrera no encontrada")

    carrera.nombre_carrera = data.get("edit_nombre")
    carrera.slug_carrera = generar_slug(carrera.nombre_carrera, str(id_carrera))

    return carrera



def eliminar_carrera_service(id_carrera):
    carrera = Carreras.query.get(id_carrera)
    if not carrera:
        raise NotFoundError("Carrera no encontrada")

    db.session.delete(carrera)
    return None