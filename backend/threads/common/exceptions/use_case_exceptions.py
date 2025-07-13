from threads.common.base_exception import BaseAppException

# --- Use Case 層錯誤 ---
class BusinessRuleViolation(BaseAppException):
    def __init__(self, message):
        super().__init__(message)
    
    def to_response(self):
        return {
            "message": self.message,
            "type": self.type_name,
        }

# 子類別 — 可在不同 Use Case 中進一步分類
class InvalidObject(BusinessRuleViolation):
    def __init__(self, message):
        super().__init__(message)

class UnauthorizedAction(BusinessRuleViolation):
    def __init__(self, message):
        super().__init__(message)

class NotFound(BusinessRuleViolation):
    def __init__(self, message):
        super().__init__(message)

class AlreadyExist(BusinessRuleViolation):
    def __init__(self, message):
        super().__init__(message)

class ServiceUnavailable(BusinessRuleViolation):
    def __init__(self, message):
        super().__init__(message)