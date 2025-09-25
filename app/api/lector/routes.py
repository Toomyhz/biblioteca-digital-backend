from flask import Blueprint, request, send_file, Response, jsonify
import os
from app.config import Config
lector_bp = Blueprint('lector', __name__)


@lector_bp.route('/libro/<int:id_libro>/total_paginas', methods=['GET'])
def get_total_pages(id_libro):
    ruta_pdf = os.path.join(Config.IMAGE_CACHE_FOLDER, str(id_libro))

    if not os.path.exists(ruta_pdf):
        return jsonify({"error": "El libro no existe"}), 404
    
    try:
        todos_los_archivos = os.listdir(ruta_pdf)
        total_paginas = len(todos_los_archivos)
        return jsonify({"total_paginas": total_paginas}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@lector_bp.route('/libro/<int:id_libro>/<int:page_num>', methods=['GET'])
def get_page(id_libro, page_num):
    ruta = os.path.join(Config.IMAGE_CACHE_FOLDER, str(id_libro))
    imagen_path = os.path.join(ruta, f"pagina-{page_num}.jpg")

    if os.path.exists(imagen_path):
        return send_file(imagen_path, mimetype='image/jpeg')
    else:
        return Response("Página no encontrada", status=404)
    


@lector_bp.route('/libro/<int:id_libro>', methods=['GET'])
def get_libro(id_libro):
    if id_libro == 1:
        ruta = os.path.join(Config.PDF_UPLOAD_FOLDER, "AJEDREZ-ELEMENTOS-DE-TACTICA.pdf")
    elif id_libro == 2:
        ruta = os.path.join(Config.PDF_UPLOAD_FOLDER, "1984.pdf")
    elif id_libro == 3:
        ruta = os.path.join(Config.PDF_UPLOAD_FOLDER, "LLL.pdf")
    else:
        return {"error": "Libro no encontrado"}, 404

    rango = request.headers.get('Range', None)

    if not rango:  # descarga completa si no hay Range
        return send_file(ruta, mimetype="application/pdf")

    size = os.path.getsize(ruta)
    start, end = rango.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else size - 1

    with open(ruta, "rb") as f:
        f.seek(start)
        data = f.read(end - start + 1)

    resp = Response(data, 206, mimetype="application/pdf")
    resp.headers.add("Content-Range", f"bytes {start}-{end}/{size}")
    resp.headers.add("Accept-Ranges", "bytes")
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp