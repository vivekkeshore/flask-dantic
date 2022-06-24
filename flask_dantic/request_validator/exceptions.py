class RequestValidationError(Exception):
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message
