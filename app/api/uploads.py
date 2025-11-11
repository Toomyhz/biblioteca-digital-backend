from flask import Blueprint, send_from_directory, current_app

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/portadas/<path:filename>')
def servir_portada(filename):
    """
    Sirve un archivo de imagen de portada.
    """
    # Lee la ruta desde la config de Flask
    portada_folder = current_app.config['PORTADA_UPLOAD_FOLDER']
    
    # send_from_directory es la forma SEGURA de servir archivos
    return send_from_directory(portada_folder, filename)

@uploads_bp.route('/pdfs/<path:filename>')
def servir_pdf(filename):
    """
    Sirve un archivo PDF.
    """
    pdf_folder = current_app.config['PDF_UPLOAD_FOLDER']
    return send_from_directory(pdf_folder, filename)