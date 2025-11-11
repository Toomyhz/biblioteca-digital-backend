from flask import request
from app.extensions import db
from app.api.libros.services import (agregar_libro_service, actualizar_libro_service
                                    , eliminar_libro_service, listar_libros_service
                                    , actualizar_archivo_libro_service)
from app.api.exceptions import ServiceError, NotFoundError


def agregar_libro(data):
    try:
        nuevo_libro = agregar_libro_service(data)
        db.session.commit()
        return {"mensaje":"Libro agregado correctamente","libro":nuevo_libro}, 201
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Error en el controlador al agregar libro: {str(e)}")
    
def actualizar_archivo_libro(id_libro, archivo_pdf):
    try:
        libro_actualizado = actualizar_archivo_libro_service(id_libro, archivo_pdf)
        
        db.session.commit()

        return {'mensaje': 'Archivo subido y portada generada correctamente','libro': libro_actualizado}

    except (NotFoundError, ServiceError) as e:
        db.session.rollback()
        raise e # Vuelve a lanzar para que el Resource lo atrape
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f'Error inesperado en el controlador: {str(e)}')


def listar_libros(pagina,limite,busqueda):
    try:
        data = listar_libros_service(pagina,limite,busqueda)
        return data
    except Exception as e:
        raise ServiceError(f"Error al listar libros: {e}")
    
def actualizar_libro(id_libro):
    data = request.form
    archivo = request.files
    response, status = actualizar_libro_service(id_libro, data, archivo)
    return response, status

def eliminar_libro(id_libro):
    try:
        libro = eliminar_libro_service(id_libro)
        db.session.commit()
        return {"mensaje":"Libro eliminado correctamente","libro": libro}
    except Exception as e:
        raise ServiceError(f"Error al eliminar libro: {e}")
