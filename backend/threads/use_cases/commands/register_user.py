import hashlib
from threads.domain.entities import User as DomainUser
from threads.domain.repository import UserRepository

from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.use_case_exceptions import InvalidObject, AlreadyExist, ServiceUnavailable
from threads.common.exceptions.repository_exceptions import EntityAlreadyExists, EntityOperationFailed, InvalidEntityInput
class RegisterUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    def execute(self, username: str, email: str, password: str) -> DomainUser:

        if password is None or len(password) < 3:
            raise InvalidObject(message="密碼必須至少8個字元")
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            new_user = DomainUser(id=None, username=username, email=email, hashed_password=hashed_password)
        except DomainValidationError as e:
            raise InvalidObject(message=e.message)
        
        try:
            return self.user_repository.create_user(new_user)
        except EntityAlreadyExists as e:
            raise AlreadyExist(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
