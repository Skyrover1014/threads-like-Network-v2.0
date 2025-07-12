from threads.domain.repository import PostRepository
from threads.domain.entities import Post as DomainPost
from typing import List

from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject

class GetProfilePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self,auth_user_id:int, author_id:int, offset:int, limit:int) -> List[DomainPost]: 
        try:
            return self.post_repository.get_posts_by_author_id(auth_user_id, author_id, offset, limit)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)