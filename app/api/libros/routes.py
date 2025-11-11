from flask_restx import Namespace, Resource
from werkzeug.datastructures import FileStorage
from .models import register_libro_models
from .controllers import actualizar_libro,agregar_libro,eliminar_libro,listar_libros, actualizar_archivo_libro
from app.api.exceptions import NotFoundError, ServiceError
from flask import request
# Namespace
libros_sn = Namespace('libros',description="Operaciones relacionadas con libros")
models = register_libro_models(libros_sn)

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
        return listar_libros(pagina,limite,busqueda)
    
    @libros_sn.doc("create_book")
    @libros_sn.expect(models["input"],validate=True)
    @libros_sn.marshal_with(models["response"], code=201)
    def post(self):
        '''Agregar nuevo libro'''
        data = libros_sn.payload
        return agregar_libro(data)


@libros_sn.route("/<int:id_libro>")
@libros_sn.param("id_libro", "El identificador del libro")
class Libro(Resource):
    @libros_sn.doc("update_book")
    @libros_sn.expect(models["update"],validate=True)
    @libros_sn.marshal_with(models["response"])
    def put(self,id_libro):
        '''Actualizar un libro existente'''
        data = libros_sn.payload 
        return actualizar_libro(data)

    @libros_sn.doc("delete_book")
    @libros_sn.marshal_with(models["response"])
    def delete(self, id_libro):
        '''Eliminar un libro'''
        return eliminar_libro(id_libro)
    
@libros_sn.route('/<int:id_libro>/archivo')
@libros_sn.param('id_libro', 'El ID del libro')
class LibroArchivoResource(Resource):
    @libros_sn.doc('subir_archivo_pdf')
    @libros_sn.expect(archivo_parser) 
    @libros_sn.marshal_with(models['response'], code=200) 
    @libros_sn.response(404, 'Libro no encontrado', models['error'])
    def put(self, id_libro):
        """
        PASO 2: Sube el PDF de un libro y genera la portada.
        """
        args = archivo_parser.parse_args()
        archivo_pdf = args['pdf'] 
        
        try:
            return actualizar_archivo_libro(id_libro, archivo_pdf)
        
        except NotFoundError as e:
            libros_sn.abort(404, str(e))
        except ServiceError as e:
            libros_sn.abort(400, str(e))
        except Exception as e:
            libros_sn.abort(500, str(e))