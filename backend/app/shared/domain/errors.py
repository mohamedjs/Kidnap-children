"""Domain errors. The HTTP layer maps each one to a status code and the error envelope."""


class DomainError(Exception):
    code = "domain_error"
    status = 400

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class Invalid(DomainError):
    code = "invalid"
    status = 422


class NotFound(DomainError):
    code = "not_found"
    status = 404


class Forbidden(DomainError):
    code = "forbidden"
    status = 403


class Unauthorized(DomainError):
    code = "unauthorized"
    status = 401


class Conflict(DomainError):
    code = "conflict"
    status = 409
