# app/api/carreras/models.py
from flask_restx import fields


def register_carrera_models(api):
    carrera_input = api.model('CarreraInput', {
        'new_nombre_carrera': fields.String(
            required=True, description='Nombre de la carrera',
            example='Pedagogía en Matemáticas', min_length=3, max_length=255
        ),
    })

    carrera_update = api.model('CarreraUpdate', {
        'edit_nombre_carrera': fields.String(
            required=False, description='Nuevo nombre de la carrera',
            example='Pedagogía en Matemáticas Aplicadas', min_length=3, max_length=255
        ),
    })

    carrera = api.model('Carrera', {
        'id_carrera': fields.Integer(description='ID único', example=1),
        'nombre_carrera': fields.String(example='Pedagogía en Matemáticas'),
        'slug_carrera': fields.String(example='pedagogia-en-matematicas')
    })

    response = api.model('CarreraResponse', {
        'mensaje': fields.String(example='Carrera agregada correctamente'),
        'carrera': fields.Nested(carrera)
    })

    lista = api.model('CarrerasListResponse', {
        'data': fields.List(fields.Nested(carrera))
    })

    error = api.model('Error', {
        'error': fields.String(example='Carrera no encontrada')
    })

    return {
        'input': carrera_input,
        'update': carrera_update,
        'single': carrera,
        'response': response,
        'list': lista,
        'error': error,
    }
