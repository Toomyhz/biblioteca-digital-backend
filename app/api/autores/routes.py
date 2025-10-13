from flask import Blueprint, request
from app.api.auth.access_control import roles_required



from flask_restx import Namespace, Resource
# Namespace
autores_sn = Namespace('autores',description="Operaciones relacionadas con los autores")

# "Resource" para la colección
@autores_sn.route("/")
class AutorList(Resource):
    @autores_sn.doc("list_autores")
    def get(self):
        '''Listar todos los autores'''
        from app.api.autores.controllers import listar_autores
        return listar_autores()
    
    def post(self):
        '''Agregar nuevo autor'''
        from app.api.autores.controllers import agregar_autor
        return agregar_autor()

@autores_sn.route("/<int:id_autor>")
@autores_sn.param("id_autor", "El identificador del autor")
class Autor(Resource):
    def put(self,id_autor):
        '''Actualizar autor existente'''
        id_autor = str(id_autor)
        from app.api.autores.controllers import actualizar_autor
        return actualizar_autor(id_autor)

    def delete(self, id_autor):
        '''Eliminar un autor'''
        id_autor = str(id_autor)
        from app.api.autores.controllers import eliminar_autor
        return eliminar_autor(id_autor)








