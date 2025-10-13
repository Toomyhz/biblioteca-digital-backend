from flask_restx import Namespace, Resource


# Namespace
libros_sn = Namespace('libros',description="Operaciones relacionadas con libros")

# "Resource" para la colección
@libros_sn.route("/")
class LibroList(Resource):
    @libros_sn.doc("list_books")
    def get(self):
        '''Listar todos los libros'''
        from .controllers import listar_libros
        return listar_libros()
    
    def post(self):
        '''Agregar nuevo libro'''
        from .controllers import agregar_libro
        return agregar_libro()


@libros_sn.route("/<int:id_libro>")
@libros_sn.param("id_libro", "El identificador del libro")
class Libro(Resource):
    def put(self,id_libro):
        '''Actualizar un libro existente'''
        id_libro = str(id_libro)
        from .controllers import actualizar_libro
        return actualizar_libro(id_libro)

    def delete(self, id_libro):
        '''Eliminar un libro'''
        id_libro = str(id_libro)
        from .controllers import eliminar_libro
        return eliminar_libro(id_libro)

# Endpoint para home
@libros_sn.route("/home/")
class LibroHome(Resource):
    def get(self):
        '''Endpoint especifico para los libros del home'''
        from .controllers import libros_home
        return libros_home()