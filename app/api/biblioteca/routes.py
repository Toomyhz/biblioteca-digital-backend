from flask import Blueprint
from flask_restx import Resource, Namespace

biblioteca_ns = Namespace("biblioteca", description="Menejo de catálogo y búsqueda")

@biblioteca_ns.route("/")
class Biblioteca(Resource):
    @biblioteca_ns.doc("get_biblioteca")
    def get(self):
        '''Retorno de libros para el catalogo'''
        from .controllers import listado_biblioteca
        return listado_biblioteca()