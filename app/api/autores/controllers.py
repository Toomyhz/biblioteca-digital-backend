from flask import request
from app.api.autores.services import agregar_autor_service, actualizar_autor_service, eliminar_autor_service, listar_autores_service


def agregar_autor():
    data = request.get_json()
    response, status = agregar_autor_service(data)
    return(response), status


def listar_autores():
    response, status = listar_autores_service()
    return(response), status


def actualizar_autor(id_autor):
    data = request.get_json()
    response, status = actualizar_autor_service(id_autor, data)

    if not id_autor:
        return({'error': 'El ID del autor es obligatorio'}), 400
    elif status != 200:
        return({'error': response}), status

    return (response), status


def eliminar_autor(id_autor):
    response, status = eliminar_autor_service(id_autor)

    if not id_autor:
        return ({'error': 'El ID del autor es obligatorio'}), 400
    elif status != 200:
        return ({'error': response}), status

    return (response), status
