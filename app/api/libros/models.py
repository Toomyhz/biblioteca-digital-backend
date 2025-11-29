from flask_restx import fields

# Diccionario base de descripciones
diccionario_libro = {
    "id_libro": "ID único del libro",
    "titulo": "Titulo del libro",
    "isbn": "ISBN del libro",
    "anio_publicacion": "Año de publicación del libro",
    "estado": "Estado de visibilidad del libro",
    "ids_autores": "Lista de IDs de autores",
    "ids_carreras": "Lista de IDs de carreras",
    "archivo_pdf": "Ruta al PDF del libro",
    "archivo_portada": "Ruta a la portada del libro",
    "slug_titulo": "Slug del libro",
    "visualizaciones": "Número de clicks hechos en el libro",
    "fecha_creacion": "Fecha de creación del libro"
}


def register_libro_models(api):

    autor_nested = api.model('AutorNested', {
        'id_autor': fields.Integer(),
        'nombre_completo': fields.String(example='Juan Pérez')
    })

    carrera_nested = api.model('CarreraNested', {
        'id_carrera': fields.Integer(),
        'nombre_carrera': fields.String(example='Pedagogía en Matemáticas')
    })


    libro_input = api.model('LibroInput', {
        "titulo": fields.String(
            required=True,
            description=diccionario_libro["titulo"],
            example="Matemáticas para dummies"
        ),
        "isbn": fields.String(
            required=False,
            description=diccionario_libro["isbn"],
            example="99xxxxxxx"
        ),
        "anio_publicacion": fields.Integer(
            required=False,
            description=diccionario_libro["anio_publicacion"],
            example=2009
        ),
        "estado": fields.String(
            required=False,
            description=diccionario_libro["estado"],
            example="disponible"  
        ),
        "ids_autores": fields.List( 
            fields.Integer,
            description=diccionario_libro["ids_autores"]
        ),
        "ids_carreras": fields.List( 
            fields.Integer,
            description=diccionario_libro["ids_carreras"]
        ),
    })


    libro_update = api.model('LibroUpdate', {
        "titulo": fields.String(
            required=False,  # 
            description=diccionario_libro["titulo"]
        ),
        "isbn": fields.String(
            required=False,
            description=diccionario_libro["isbn"]
        ),
        "anio_publicacion": fields.Integer(
            required=False,
            description=diccionario_libro["anio_publicacion"]
        ),
        "estado": fields.String(
            required=False,
            description=diccionario_libro["estado"]
        ),
        "ids_autores": fields.List(
            fields.Integer,
            required=False,
            description=diccionario_libro["ids_autores"]
        ),
        "ids_carreras": fields.List(
            fields.Integer,
            required=False,
            description=diccionario_libro["ids_carreras"]
        ),
    })


    libro = api.model('Libro', {
        "id_libro": fields.Integer(description=diccionario_libro["id_libro"]),
        "titulo": fields.String(description=diccionario_libro["titulo"]),
        "isbn": fields.String(description=diccionario_libro["isbn"]),
        "anio_publicacion": fields.Integer(description=diccionario_libro["anio_publicacion"]),
        "estado": fields.String(description=diccionario_libro["estado"]),
        "archivo_pdf": fields.String(description=diccionario_libro["archivo_pdf"]),
        "archivo_portada": fields.String(description=diccionario_libro["archivo_portada"]),
        "slug_titulo": fields.String(description=diccionario_libro["slug_titulo"]),
        "fecha_creacion": fields.String(description=diccionario_libro["fecha_creacion"]),
        "visualizaciones": fields.Integer(description=diccionario_libro["visualizaciones"]),
        "autores": fields.List(fields.Nested(autor_nested)),
        "carreras": fields.List(fields.Nested(carrera_nested))
    })

    libro_reciente_response = api.model('LibrosRecientesResponse', {
        "mensaje": fields.String(description="Mensaje de respuesta"),
        "data": fields.List(fields.Nested(libro))
    })

    response = api.model('LibroResponse', {  
        'mensaje': fields.String(example='Operación exitosa'),
        'libro': fields.Nested(libro)  
    })

    paginacion = api.model('Paginacion', {
        "pagina": fields.Integer(description="Página actual", example=1),
        "limite": fields.Integer(description="Resultados por página", example=10),
        "total": fields.Integer(description="Total de resultados", example=100),
        "total_paginas": fields.Integer(description="Total de páginas", example=10)
    })
   
    lista = api.model('LibroListResponse', {
        'data': fields.List(fields.Nested(libro)),
        "paginacion": fields.Nested(paginacion,description="Metadatos de paginación")
    })

 
    error = api.model('ErrorLibro', { 
        'error': fields.String(example='Libro no encontrado')
    })

    return {
        'input': libro_input,
        'update': libro_update,  
        'single': libro,
        'response': response,
        'list': lista,
        'libro_reciente_response': libro_reciente_response,
        'error': error,
    }