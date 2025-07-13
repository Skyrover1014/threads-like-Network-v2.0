
# === 基底錯誤類 ===
class BaseAppException(Exception):
    def __init__(self, message):
        self.message = message
        self.type_name = self.__class__.__name__
        super().__init__(message)
    
    def to_response(self):
        return {
            "message": self.message,
            "type": self.type_name
        }

# --- Domain 層錯誤 ---
class DomainValidationError(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

# --- Repository 層錯誤 ---
class EntityAlreadyExists(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class EntityDoesNotExist(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class EntityOperationFailed(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class InvalidOperation(BaseAppException):
    def __init__(self, message):
        super().__init__(message)

class InvalidEntityInput(BaseAppException):
    def __init__(self, message):
        super().__init__(message)


# --- Use Case 層錯誤 ---
class BusinessRuleViolation(BaseAppException):
    def __init__(self, message, reason=None):
        self.reason = reason
        super().__init__(message)
    
    def to_response(self):
        return {
            "message": self.message,
            "reason": self.reason,
            "type": self.type_name
        }

# 子類別 — 可在不同 Use Case 中進一步分類
class PostNotFound(BusinessRuleViolation):
    def __init__(self, message="找不到貼文"):
        super().__init__(message, reason="not_found")

class InvalidPostContent(BusinessRuleViolation):
    def __init__(self, message="貼文內容不符合格式"):
        super().__init__(message, reason="invalid_content")

class UnauthorizedAction(BusinessRuleViolation):
    def __init__(self, message="無權進行此操作"):
        super().__init__(message, reason="unauthorized")

