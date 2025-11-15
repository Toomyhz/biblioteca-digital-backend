from flask import request, send_file, Response
import os
from app.config import Config

from flask_restx import Resource, Namespace

lector_ns = Namespace("lector",description="Entrega de pdfs para lector")


@lector_ns.route("/libro/<int:id_libro>")
@lector_ns.param("id_libro", "El identificador del libro")
class Lector(Resource):
    @lector_ns.doc("lector_libro")
    def get(self,id_libro):
        '''Retorno pdf de libro'''
        if id_libro == 1:
            ruta = os.path.join(Config.PDF_UPLOAD_FOLDER, "ajedrez-cambiante-26.pdf")
        elif id_libro == 2:
            ruta = os.path.join(Config.PDF_UPLOAD_FOLDER, "1984.pdf")
        elif id_libro == 3:
            ruta = os.path.join(Config.PDF_UPLOAD_FOLDER, "LLL.pdf")
        else:
            return {"error": "Libro no encontrado"}, 404
    
        return send_file(ruta, mimetype="application/pdf")
