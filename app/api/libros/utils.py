# app/utils/pdf_utils.py
import io
import os
import tempfile
import fitz  # PyMuPDF

from app.extensions import cloud_storage
from app.api.exceptions import ServiceError  

def procesar_pdf_y_subir(archivo_pdf, slug_titulo: str) -> tuple[str, str]:
    """
    Lee un archivo PDF (file-like), genera portada y sube ambos a cloud_storage.
    Devuelve (key_pdf, key_portada).

    Lanza ServiceError(…, 400) si algo falla al procesar.
    """
    key_pdf = f"libros/{slug_titulo}.pdf"
    key_portada = f"portadas/{slug_titulo}_portada.jpg"

    temp_pdf_path = None

    try:
        pdf_bytes = archivo_pdf.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            temp_pdf_path = tmp.name

        # Procesar portada
        doc = fitz.open(temp_pdf_path)
        page = doc[0]
        matriz = fitz.Matrix(0.3, 0.3)
        pix = page.get_pixmap(matrix=matriz, alpha=False)
        portada_bytes = pix.tobytes("jpg")
        doc.close()

        # Subir PDF
        cloud_storage.upload_file(
            temp_pdf_path,
            key_pdf,
            content_type="application/pdf",
            acl="private",
        )

        # Subir portada
        cloud_storage.upload_file(
            io.BytesIO(portada_bytes),
            key_portada,
            content_type="image/jpeg",
            acl="public-read",
        )

        return key_pdf, key_portada

    except Exception as e:
        raise ServiceError(f"Error al procesar el PDF: {str(e)}", 400)

    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
