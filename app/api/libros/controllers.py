from app.extensions import db
from app.api.libros.services import (agregar_libro_service, actualizar_libro_metadata_service, actualizar_libro_archivo_service
                                    , eliminar_libro_service, listar_libros_service,obtener_libro_service)
from app.api.exceptions import ServiceError, NotFoundError
import os

def agregar_libro(data,archivo_pdf):
    try:
        nuevo_libro = agregar_libro_service(data,archivo_pdf)
        db.session.commit()
        return {"mensaje":"Libro agregado correctamente","libro":nuevo_libro}, 201
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Error en el controlador al agregar libro: {str(e)}")
    
def listar_libros(pagina,limite,busqueda):
    try:
        data = listar_libros_service(pagina,limite,busqueda)
        return data
    except Exception as e:
        raise ServiceError(f"Error al listar libros: {e}")
    
def obtener_libro_por_id(id_libro):
    """
    Controlador para obtener un libro por ID (sin UoW)
    """
    try:
        libro = obtener_libro_service(id_libro)
  
        return {
            'mensaje': 'Libro obtenido correctamente',
            'libro': libro
        }
    except Exception as e:
        raise e
    
def actualizar_libro(id_libro, data):
    try:
        libro_actualizado = actualizar_libro_metadata_service(id_libro, data)
        db.session.commit()

        return {"mensaje":"Libro actualizado correctamente","libro":libro_actualizado}, 200
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Error en el controlador al agregar libro: {str(e)}")

def actualizar_archivo_libro(id_libro, archivo_pdf):
    try:
        libro_actualizado = actualizar_libro_archivo_service(id_libro, archivo_pdf)
        db.session.commit()
        respuesta =  {'mensaje': 'Archivo y portada actualizados correctamente',
            'libro': libro_actualizado}
        return respuesta 
    
    except Exception as e:
        db.session.rollback()
        raise e     

def eliminar_libro(id_libro):
    try:
        libro = eliminar_libro_service(id_libro)
        db.session.commit()
        return {"mensaje":"Libro eliminado correctamente","libro": libro}
    except Exception as e:
        raise ServiceError(f"Error al eliminar libro: {e}")
