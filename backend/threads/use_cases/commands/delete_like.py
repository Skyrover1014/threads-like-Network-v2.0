from threads.domain.entities import Like as DomainLike
from threads.domain.repository import LikeRepository
from typing import Literal

from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, InvalidEntityInput, EntityOperationFailed, InvalidOperation
from threads.common.exceptions.use_case_exceptions import NotFound, UnauthorizedAction, InvalidObject, ServiceUnavailable

class DeleteLike:
    def __init__(self, like_repository: LikeRepository):
        self.like_repository = like_repository
    
    def execute(self, user_id, content_id, content_type, deleter) -> None:
        try:
            domain_like = self.like_repository.get_like_by_id(user_id, content_id, content_type)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
             

        try: 
            domain_like.verify_deletable_by(deleter)
        except DomainValidationError as e:
            raise UnauthorizedAction(message=e.message)
        
        try:
            return self.like_repository.delete_like(domain_like)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidOperation as e:
            raise InvalidObject(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
