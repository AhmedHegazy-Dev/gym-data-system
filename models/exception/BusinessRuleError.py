from .GymException import GymException

class BusinessRuleError(GymException):
    def __init__(self, message: str, code: int):
        super().__init__(message, code)

    def __str__(self):
        return f"[BusinessRuleError] {self.code} {self.message}"