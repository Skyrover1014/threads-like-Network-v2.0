from threads.common.base_exception import BaseAppException



class EntityAlreadyExists(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class EntityDoesNotExist(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class EntityOperationFailed(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class InvalidEntityInput(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class InvalidOperation(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

