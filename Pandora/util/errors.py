from custom_logger import Color as c

class PandoraException(Exception):
    def __init__(self, message) -> None:
        self.message = f"{c.red} {message}"
        super().__init__(self.message)
        
class NameNotDropping(PandoraException):
    pass

class InvalidAccounts(PandoraException):
    pass