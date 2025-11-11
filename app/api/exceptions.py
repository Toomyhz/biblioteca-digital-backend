class RegistroExistenteError(Exception):
    pass

class NotFoundError(Exception):
    pass

class ServiceError(Exception):
    """Error genérico de servicio."""
    status_code = 500

    def __init__(self, message="Error interno del servicio", status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message