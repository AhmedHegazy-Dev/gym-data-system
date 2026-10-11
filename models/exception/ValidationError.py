from .GymException import GymException

class ValidationError(GymException):
    def __init__(self, message: str, code: int):
        super().__init__(message, code)

    def __str__(self):
        return f"[ValidationError] {self.code} {self.message}"