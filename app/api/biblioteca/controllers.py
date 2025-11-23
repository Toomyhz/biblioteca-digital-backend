from .services import listar_libros_biblioteca, diccionario_catalogo_service

def listado_biblioteca():
    response, status = listar_libros_biblioteca()
    return response, status

def diccionario_catalogo():
    response, status = diccionario_catalogo_service()
    return response, status
