from flask import Blueprint, send_from_directory, current_app, jsonify, redirect
from app.extensions import cloud_storage
from app.models.libros import Libros

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/leer/<int:id_libro>')
def get_presigned_url(id_libro):
    """
    Sirve un archivo PDF.
    """
    libro = Libros.query.get_or_404(id_libro)

    if not libro.archivo_pdf:
        return jsonify({"mensaje": "El libro no tiene un archivo PDF asociado."}), 404
    
    url_firmada = cloud_storage.get_presigned_url(libro.archivo_pdf, expiration=30)
    if not url_firmada:
        return jsonify({"mensaje": "No se pudo generar la URL del archivo."}), 500
    return jsonify({
    'status': 'success',
    'url': url_firmada
})