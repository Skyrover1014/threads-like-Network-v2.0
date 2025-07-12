from threads.domain.repository import PostRepository
from threads.domain.entities import Post as DomainPost
from typing import Optional

from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject

class GetPostById:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self, post_id:int, auth_user_id:int) -> Optional[DomainPost]:
        try:
            return self.post_repository.get_post_by_id(post_id, auth_user_id)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)