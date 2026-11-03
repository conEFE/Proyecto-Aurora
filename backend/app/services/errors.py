"""Errores de dominio que las rutas traducen a HTTP."""


class DomainError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class ForbiddenError(DomainError):
    status_code = 403


class ValidationError(DomainError):
    status_code = 422
