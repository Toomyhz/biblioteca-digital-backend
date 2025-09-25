from flask import Blueprint, request, send_file, Response
import os
from app import Config
lector_bp = Blueprint('lector', __name__)

@lector_bp.route('/libro/test/', methods=['GET'])
def get_page():
    ruta = Config.PDF_UPLOAD_FOLDER + "/AJEDREZ-ELEMENTOS-DE-TACTICA.pdf"
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