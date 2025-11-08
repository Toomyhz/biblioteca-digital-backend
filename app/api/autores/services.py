from app.models.autores import Autores
from app.api.utils.helpers import generar_slug
from app.extensions import db

from app.api.exceptions import NotFoundError, RegistroExistenteError

def agregar_autor_service(data):
    nombre_completo = data.get("nombre_completo")
    nacionalidad = data.get("nacionalidad")
    
    # Validar duplicado
    existente = Autores.query.filter_by(nombre_completo=nombre_completo).first()
    if existente:
        raise RegistroExistenteError("Ya existe un autor con ese nombre.")
    
    # Crear autor
    slug_autor = generar_slug(nombre_completo)
    nuevo_autor = Autores(
        nombre_completo=nombre_completo,
        nacionalidad=nacionalidad,
        slug_autor=slug_autor
    )
    
    db.session.add(nuevo_autor)
    db.session.flush()

    # Actualizar slug con ID
    nuevo_autor.slug_autor = generar_slug(nombre_completo,str(nuevo_autor.id_autor))
    return nuevo_autor

def listar_autores_service(busqueda = None):
    query = db.session.query(Autores)
    if busqueda:
            patron = f"%{busqueda}%"
            query = query.filter(
        (Autores.nombre_completo.ilike(patron)) |
        (Autores.nacionalidad.ilike(patron))
            )
    autores = query.order_by(Autores.id_autor.asc()).all()
    return [autor.to_dict_basic() for autor in autores]

def actualizar_autor_service(id_autor, data):
    autor = Autores.query.get(id_autor)
    if not autor:
        raise NotFoundError("Autor no encontrado.")
    
    nombre_completo = data.get("nombre_completo")
    nacionalidad = data.get("nacionalidad")
    slug_autor = generar_slug(nombre_completo, id_autor)
    
    autor.nombre_completo = nombre_completo
    autor.nacionalidad = nacionalidad
    autor.slug_autor = slug_autor

    return autor


def eliminar_autor_service(id_autor):
        autor = Autores.query.get(id_autor)
        if not autor:
            raise NotFoundError("El id no pertenece a ningún autor.")

        db.session.delete(autor)
        return None
