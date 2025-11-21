from flask_restx import Namespace, Resource, reqparse
from .controllers import (
    listar_carreras, agregar_carrera,
    actualizar_carrera, eliminar_carrera
)
from .models import register_carrera_models

carreras_sn = Namespace(
    'carreras', description="Operaciones relacionadas con las carreras académicas"
)

models = register_carrera_models(carreras_sn)

parser = reqparse.RequestParser()


@carreras_sn.route("/")
class CarreraList(Resource):
    @carreras_sn.expect(parser)
    @carreras_sn.marshal_with(models['list'], code=200)
    def get(self):
        """Listar todas las carreras"""
        return listar_carreras()

    @carreras_sn.expect(models['input'], validate=True)
    @carreras_sn.marshal_with(models['response'], code=201)
    def post(self):
        """Agregar nueva carrera"""
        return agregar_carrera()


@carreras_sn.route("/<int:id_carrera>")
@carreras_sn.param("id_carrera", "ID de la carrera")
class Carrera(Resource):

    @carreras_sn.expect(models['update'], validate=True)
    @carreras_sn.marshal_with(models['response'], code=200)
    def put(self, id_carrera):
        """Actualizar carrera existente"""
        data = carreras_sn.payload
        return actualizar_carrera(id_carrera,data)

    @carreras_sn.marshal_with(models['response'], code=200)
    def delete(self, id_carrera):
        """Eliminar una carrera"""
        return eliminar_carrera(id_carrera)
