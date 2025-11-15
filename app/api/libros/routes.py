from flask_restx import Namespace, Resource
from werkzeug.datastructures import FileStorage
from flask import request

from .models import register_libro_models
from app.api.exceptions import NotFoundError, ServiceError

from .controllers import actualizar_libro,agregar_libro,eliminar_libro,listar_libros, actualizar_archivo_libro, obtener_libro_por_id

# Namespace
libros_sn = Namespace('libros',description="Operaciones relacionadas con libros")
models = register_libro_models(libros_sn)

# Parser para crear
libro_parser = libros_sn.parser()
libro_parser.add_argument('titulo', type=str, required=True, location='form')
libro_parser.add_argument('isbn', type=str, location='form')
libro_parser.add_argument('anio_publicacion', type=int, location='form')
libro_parser.add_argument('estado', type=str, location='form')
libro_parser.add_argument('ids_autores', type=int, action='append', location='form')
libro_parser.add_argument('ids_carreras', type=int, action='append', location='form')
libro_parser.add_argument('pdf', type=FileStorage, required=True, location='files')

# Parser para actualizar archivo
archivo_parser = libros_sn.parser()
archivo_parser.add_argument("pdf",type=FileStorage,required=True,location="files",help="Archivo PDF del libro")


# "Resource" para la colección
@libros_sn.route("/")
class LibroList(Resource):

    @libros_sn.doc("list_books")
    @libros_sn.param("pagina", "Número de página", type=int, default=1)
    @libros_sn.param("limite", "Resultados por página", type=int, default=10)
    @libros_sn.param("busqueda", "Término de búsqueda", type=str)
    @libros_sn.marshal_with(models["list"])
    def get(self):
        '''Listar todos los libros'''
        pagina = request.args.get("pagina",1,type=int)
        limite = request.args.get("limite",10,type=int)
        busqueda = request.args.get("busqueda",None,type=str)
        try:
            return listar_libros(pagina,limite,busqueda)
        except Exception as e:
            libros_sn.abort(500, f"Error al listar libros: f{str(e)}")
    
    @libros_sn.doc("create_book")
    @libros_sn.expect(libro_parser)
    @libros_sn.marshal_with(models["response"], code=201)
    def post(self):
        '''Agregar nuevo libro'''
        args = libro_parser.parse_args()

        archivo_pdf = args.pop("pdf",None)
        data = args
        try:
            return agregar_libro(data,archivo_pdf)
        except ServiceError as e:
            libros_sn.abort(e.status_code, e.message)
        except Exception as e:
            libros_sn.abort(500,str(e))
            


@libros_sn.route("/<int:id_libro>")
@libros_sn.param("id_libro", "El identificador del libro")
class Libro(Resource):

    @libros_sn.doc("get_book_by_id")
    @libros_sn.marshal_with(models["response"]) # Reutiliza tu modelo de respuesta
    @libros_sn.response(404, 'Libro no encontrado', models["error"])
    def get(self, id_libro):
        '''Obtener un libro por su ID'''
        try:
            # Llama al nuevo controlador
            return obtener_libro_por_id(id_libro)
        except NotFoundError as e:
            libros_sn.abort(404, str(e))
        except Exception as e:
            libros_sn.abort(500, str(e))

    @libros_sn.doc("update_book_metadata")
    @libros_sn.expect(models["update"],validate=True)
    @libros_sn.marshal_with(models["response"])
    def put(self,id_libro):
        '''Actualizar un libro existente'''
        data = libros_sn.payload 
        try:
            return actualizar_libro(id_libro,data)
        except NotFoundError as e:
            libros_sn.abort(404, str(e))
        except ServiceError as e:
            libros_sn.abort(e.status_code,e.message)
        except Exception as e:
            libros_sn.abort(500, str(e))
        
            

    @libros_sn.doc("delete_book")
    @libros_sn.marshal_with(models["response"])
    def delete(self, id_libro):
        '''Eliminar un libro'''
        try:
            return eliminar_libro(id_libro)
        except NotFoundError as e:
            libros_sn.abort(404, str(e))    
        except ServiceError as e:
            libros_sn.abort(e.status_code, e.message)    
        except Exception as e:
            libros_sn.abort(500, str(e))    

@libros_sn.route("/<int:id_libro>/archivo")
@libros_sn.param("id_libro","El ID del libro")
class LibroArchivoResource(Resource):
    
    @libros_sn.doc("update_book_file")
    @libros_sn.expect(archivo_parser)
    @libros_sn.marshal_with(models["response"], code=200)
    @libros_sn.response(404,"libro no encontrado", models["error"])
    def put(self, id_libro):
        args = archivo_parser.parse_args()
        archivo_pdf = args["pdf"]

        try:
            return actualizar_archivo_libro(id_libro, archivo_pdf)
        except NotFoundError as e:
            libros_sn.abort(404,str(e))
        except ServiceError as e:
            libros_sn.abort(e.status_code, e.message)
        except Exception as e:
            libros_sn.abort(500,str(e))