
class GymException(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code

    def __str__(self):
        return f"[GymException] {self.code} {self.message}" 