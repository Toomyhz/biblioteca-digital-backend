from functools import wraps
from flask_restx import abort
from .errors import APIError
from flask import request
from .errors import ValidationError, NotFoundError, ConflictError, IntegrityError
from app.api.carreras.services import (
    agregar_carrera_service,
    actualizar_carrera_service,
    eliminar_carrera_service,
    leer_carreras_service,
)


def safe_controller(func):
    """Maneja errores comunes en controladores de forma uniforme."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            abort(e.status_code, e.message)
        except Exception as e:
            abort(500, f"Error inesperado: {str(e)}")
    return wrapper


def validar_id_carrera(id_carrera: str) -> int:
    """Valida que el ID sea un entero positivo."""
    try:
        id_int = int(id_carrera)
        if id_int <= 0:
            raise ValidationError("El ID debe ser un número positivo")
        return id_int
    except ValueError:
        raise ValidationError("El ID debe ser un número válido")


@safe_controller
def listar_carreras():
    """Listar todas las carreras."""
    carreras  = leer_carreras_service()
    return {"data":carreras}


@safe_controller
def agregar_carrera():
    """Agregar nueva carrera."""
    data = request.get_json() or request.form
    nombre = data.get('new_nombre_carrera', '').strip()

    if not nombre:
        raise ValidationError("El nombre de la carrera es obligatorio")
    if len(nombre) < 3:
        raise ValidationError("El nombre debe tener al menos 3 caracteres")
    if len(nombre) > 255:
        raise ValidationError("El nombre no puede exceder 255 caracteres")

    response, status = agregar_carrera_service(data)
    if status == 409:
        raise ConflictError(f"Ya existe una carrera con ese nombre: {nombre}")

    return response, status


@safe_controller
def actualizar_carrera(id_carrera):
    """Actualizar carrera existente."""
    id_int = validar_id_carrera(id_carrera)
    data = request.get_json() or request.form
    nombre = data.get('edit_nombre_carrera', '').strip()

    if nombre:
        if len(nombre) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres")
        if len(nombre) > 255:
            raise ValidationError("El nombre no puede exceder 255 caracteres")

    response, status = actualizar_carrera_service(id_int, data)
    if status == 404:
        raise NotFoundError(f"Carrera con ID {id_int} no encontrada")
    if status == 409:
        raise ConflictError("Ya existe una carrera con ese nombre")
    return response, status


@safe_controller
def eliminar_carrera(id_carrera):
    """Eliminar carrera."""
    id_int = validar_id_carrera(id_carrera)
    response, status = eliminar_carrera_service(id_int)
    if status == 404:
        raise NotFoundError(f"Carrera con ID {id_int} no encontrada")
    if "foreign key" in str(response).lower():
        raise IntegrityError(
            "No se puede eliminar la carrera porque tiene libros asociados")
    return response, status
