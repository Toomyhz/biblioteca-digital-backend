from flask_restx import fields
from . import autores_sn

# Diccionario base de descripciones
diccionario_autor = {
    "id_autor": "Identificador único del autor",
    "nombre_completo": "Nombre completo del autor",
    "nacionalidad": "País de origen del autor",
    "slug_autor": "Slug generado automáticamente para el autor",
}

# Modelo de entrada
AutorInput = autores_sn.model(
    "AutorInput",
    {
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
    },
)

# Modelo de salida (individual)
AutorOutput = autores_sn.model(
    "AutorOutput",
    {
        "id_autor": fields.Integer(description=diccionario_autor["id_autor"]),
        "nombre_completo": fields.String(description=diccionario_autor["nombre_completo"]),
        "nacionalidad": fields.String(description=diccionario_autor["nacionalidad"]),
        "slug_autor": fields.String(description=diccionario_autor["slug_autor"]),
    },
)

# Modelo de listado
AutorListM = autores_sn.model(
    "AutorList",
    {
        "id_autor": fields.Integer(description=diccionario_autor["id_autor"]),
        "nombre_completo": fields.String(description=diccionario_autor["nombre_completo"]),
        "nacionalidad": fields.String(description=diccionario_autor["nacionalidad"]),
        "slug_autor": fields.String(description=diccionario_autor["slug_autor"]),
    },
)
