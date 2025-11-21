from sqlalchemy.exc import IntegrityError,DataError
from app.extensions import db
from app.api.autores.services import agregar_autor_service, actualizar_autor_service, eliminar_autor_service, listar_autores_service
from app.api.exceptions import NotFoundError, RegistroExistenteError


def agregar_autor(data):
    """Lógica de orquestación para agregar un autor"""
    try:
        autor = agregar_autor_service(data)
        db.session.commit()
        return {"mensaje":"Autor agregado correctamente","autor":autor}, 201
    
    except RegistroExistenteError as e:
        db.session.rollback()
        raise e
    except IntegrityError:
        db.session.rollback()
        raise RegistroExistenteError("Ya existe un autor con ese slug o nombre.")
    except Exception as e:
        db.session.rollback()
        raise e
    

def listar_autores(busqueda=None):
    """Obtener todos los autores"""
    autores = listar_autores_service(busqueda)
    return {"data":autores}


def actualizar_autor(id_autor,data):
    """Actualizar un autor existente"""
    try:
        autor = actualizar_autor_service(id_autor, data)
        db.session.commit()
        return {"mensaje":"Autor actualizado correctamente","autor":autor}
    except NotFoundError as e:
        db.session.rollback()
        raise e
    except IntegrityError:
        db.session.rollback()
        raise RegistroExistenteError("El autor actualizado entra en conflicto con otro existente.")
    except Exception as e:
        db.session.rollback()
        raise e

def eliminar_autor(id_autor):
    """Eliminar un autor existente"""
    try:
        eliminar_autor_service(id_autor)
        db.session.commit()
        return {"mensaje":"Autor eliminado correctamente"}
    
    except NotFoundError as e:
        db.session.rollback()
        raise e
    
    except IntegrityError:
        db.session.rollback()
        raise RegistroExistenteError("No se puede eliminar este autor: está asociado a uno o más libros")
    
    except Exception as e:
        db.session.rollback()
        raise e
        
