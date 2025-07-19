from threads.domain.entities import Like as DomainLike
from threads.domain.repository import LikeRepository
from typing import Literal


from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.use_case_exceptions import InvalidObject, AlreadyExist, NotFound, ServiceUnavailable
from threads.common.exceptions.repository_exceptions import EntityAlreadyExists, EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput, InvalidOperation

class CreateLike:
    def __init__(self, like_repository: LikeRepository):
        self.like_repository = like_repository
    
    def execute(self,user_id: int, content_item_id:int, content_type:Literal['post', 'comment']) -> DomainLike:
        try:
            new_like = DomainLike(id=None, user_id=user_id, content_item_id=content_item_id, content_type=content_type)
        except DomainValidationError as e:
            raise InvalidObject(message=e.message)
        except TypeError as e:
            raise InvalidObject(message=f"封裝 Like 失敗: {str(e)}")
        
        try: 
            return self.like_repository.create_like(new_like)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityAlreadyExists as e:
            raise AlreadyExist(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        except InvalidOperation as e:
            raise InvalidObject(message=e.message)