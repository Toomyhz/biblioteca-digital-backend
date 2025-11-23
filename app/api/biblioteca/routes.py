from flask_restx import Resource, Namespace
from .controllers import listado_biblioteca, diccionario_catalogo

biblioteca_ns = Namespace("biblioteca", description="Menejo de catálogo y búsqueda")

@biblioteca_ns.route("/")
class Biblioteca(Resource):
    @biblioteca_ns.doc("get_biblioteca")
    def get(self):
        '''Retorno de libros para el catalogo'''
        return listado_biblioteca()

@biblioteca_ns.route("/catalogo")
class BibliotecaAutores(Resource):
    def get(self):
        '''Autores y Carreras que tienen al menos un libro'''
        return diccionario_catalogo()
    