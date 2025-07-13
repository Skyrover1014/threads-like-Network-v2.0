from threads.domain.repository import UserRepository
from threads.domain.entities import User as DomainUser
from typing import Optional

from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject

class GetUserProfile:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    def execute(self, user_id: int) -> Optional[DomainUser]:
        try:
            return self.user_repository.get_user_by_id(user_id)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)