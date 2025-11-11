from flask_restx import  Namespace, Resource
from app.api.auth.access_control import roles_required
from .models import register_autor_models
from app.api.autores.controllers import agregar_autor,actualizar_autor,eliminar_autor,listar_autores
from flask import request

autores_sn = Namespace('autores',description="Operaciones relacionadas con los autores")
models = register_autor_models(autores_sn)


# "Resource" para la colección
@autores_sn.route("/")
class AutorList(Resource):
    @autores_sn.doc("list_autores")
    @autores_sn.param(
    "busqueda",
    "Texto de búsqueda (nombre o nacionalidad del autor)",
    type=str,
    required=False
    )
    @autores_sn.marshal_with(models["list"])
    def get(self):
        '''Listar todos los autores'''
        busqueda = request.args.get("busqueda", type=str)
        return listar_autores(busqueda)
    
    @autores_sn.doc("create_autor")
    @autores_sn.expect(models["input"],validate=True)
    @autores_sn.marshal_with(models["response"])
    def post(self):
        '''Agregar nuevo autor'''
        data = autores_sn.payload
        return agregar_autor(data)

# Resource para individual
@autores_sn.route("/<int:id_autor>")
@autores_sn.param("id_autor", "El identificador del autor")
class Autor(Resource):
    @autores_sn.doc("update_autor")
    @autores_sn.expect(models["update"])
    @autores_sn.marshal_with(models["response"])
    def put(self,id_autor):
        '''Actualizar autor existente'''
        data = autores_sn.payload
        id_autor = str(id_autor)
        return actualizar_autor(id_autor,data)

    @autores_sn.doc("delete_autor")
    @autores_sn.marshal_with(models["response"])
    def delete(self, id_autor):
        '''Eliminar un autor'''
        id_autor = str(id_autor)
        return eliminar_autor(id_autor)








