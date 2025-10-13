from flask_restx import Namespace, Resource
# Namespace
carreras_sn = Namespace('carreras',description="Operaciones relacionadas con las carreras")

# "Resource" para la colección
@carreras_sn.route("/")
class CarreraList(Resource):
    @carreras_sn.doc("list_carreras")
    def get(self):
        '''Listar todas las carreras'''
        from .controllers import listar_carreras
        return listar_carreras()
    
    def post(self):
        '''Agregar nueva carrera'''
        from .controllers import agregar_carrera
        return agregar_carrera()

@carreras_sn.route("/<int:id_carrera>")
@carreras_sn.param("id_carrera", "El identificador de la carrera")
class Carrera(Resource):
    def put(self,id_carrera):
        '''Actualizar carrera existente'''
        id_carrera = str(id_carrera)
        from .controllers import actualizar_carrera
        return actualizar_carrera(id_carrera)

    def delete(self, id_carrera):
        '''Eliminar una carrera'''
        id_carrera = str(id_carrera)
        from .controllers import eliminar_carrera
        return eliminar_carrera(id_carrera)








