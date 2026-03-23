class DomainError(Exception):
    status_code = 400
    detail = "Erro de domínio."

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class NotFoundError(DomainError):
    status_code = 404
    detail = "Recurso não encontrado."


class ConflictError(DomainError):
    status_code = 409
    detail = "Conflito de negócio."
