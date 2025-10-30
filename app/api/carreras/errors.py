from flask_restx import abort


class APIError(Exception):
    """Error base para la capa API."""
    status_code = 500
    message = "Error interno del servidor"

    def __init__(self, message=None, status_code=None):
        super().__init__(message or self.message)
        self.message = message or self.message
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        return {"error": self.message}


class ServiceError(Exception):
    """Error genérico de servicio."""
    status_code = 500

    def __init__(self, message="Error interno del servicio", status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message


class ValidationError(APIError):
    status_code = 400
    message = "Error de validación"


class NotFoundError(APIError):
    status_code = 404
    message = "Recurso no encontrado"


class ConflictError(APIError):
    status_code = 409
    message = "Conflicto con datos existentes"


class IntegrityError(APIError):
    status_code = 400
    message = "Violación de integridad referencial"


def handle_api_error(error):
    """Convierte excepciones APIError en respuestas HTTP."""
    abort(error.status_code, error.message)
