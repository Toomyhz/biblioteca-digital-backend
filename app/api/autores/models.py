from flask_restx import fields
# Diccionario base de descripciones
diccionario_autor = {
    "id_autor": "Identificador único del autor",
    "nombre_completo": "Nombre completo del autor",
    "nacionalidad": "País de origen del autor",
    "slug_autor": "Slug generado automáticamente para el autor",
}


def register_autor_models(api):
    autor_input = api.model('AutorInput', {
        "nombre_completo": fields.String(
            required=True,
            description=diccionario_autor["nombre_completo"],
            example="Gabriel García Márquez"
        ),
        "nacionalidad": fields.String(
            required=False,
            description=diccionario_autor["nacionalidad"],
            example="Colombiana"
        ),
    })

    autor_update = api.model('AutorUpdate', {
        "nombre_completo": fields.String(
            required=False,
            description=diccionario_autor["nombre_completo"],
            example="Gabriel García Márquez"
        ),
        "nacionalidad": fields.String(
            required=False,
            description=diccionario_autor["nacionalidad"],
            example="Colombiana"
        ),
    })

    autor = api.model('Autor', {
        "id_autor": fields.Integer(description=diccionario_autor["id_autor"]),
        "nombre_completo": fields.String(description=diccionario_autor["nombre_completo"]),
        "nacionalidad": fields.String(description=diccionario_autor["nacionalidad"]),
        "slug_autor": fields.String(description=diccionario_autor["slug_autor"])
    })

    response = api.model('AutorResponse', {
        'mensaje': fields.String(example='Autor agregado correctamente'),
        'autor': fields.Nested(autor)
    })

    lista = api.model('AutoresListResponse', {
        'data': fields.List(fields.Nested(autor))
    })

    error = api.model('Error', {
        'error': fields.String(example='Autor no encontrado')
    })

    return {
        'input': autor_input,
        'update': autor_update,
        'single': autor,
        'response': response,
        'list': lista,
        'error': error,
    }