from app.models.autores import Autores
from app.api.utils.helpers import generar_slug
from app.models.autores import Autores
from app import db


def agregar_autor_service(data):
    try:
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
        db.session.flush()

        # Actualizar slug con ID
        nuevo_autor.slug_autor = generar_slug(
            nombre_completo,
            str(nuevo_autor.id_autor)
        )

        db.session.commit()

        return {
            'mensaje': 'Autor agregado correctamente',
            'autor': nuevo_autor.to_dict()
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al crear autor: {e}'}, 500


def listar_autores_service():
    try:
        autores = Autores.query.order_by(Autores.id_autor.asc()).all()
        autores_dict = [autor.to_dict() for autor in autores]
        return autores_dict, 200
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al leer autores: {e}'}, 500


def actualizar_autor_service(id_autor, data):
    try:
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

        return {'mensaje': 'Autor actualizado correctamente',
                'autor': autor.to_dict()
                }, 201
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al actualizar autor: {e}'}, 500


def eliminar_autor_service(id_autor):
    try:
        autor = Autores.query.get(id_autor)
        if not autor:
            return {'error': 'Autor no encontrado'}, 404

        db.session.delete(autor)
        db.session.commit()

        return {'mensaje': 'Autor eliminado correctamente',
                'autor': autor.to_dict()
                }, 200
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al eliminar autor: {e}'}, 500
