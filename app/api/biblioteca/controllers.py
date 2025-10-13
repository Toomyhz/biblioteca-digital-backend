from .services import listar_libros_biblioteca

def listado_biblioteca():
    response, status = listar_libros_biblioteca()
    return response, status