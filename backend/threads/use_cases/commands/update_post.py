from threads.domain.entities import Post as DomainPost
from threads.domain.repository import PostRepository

from threads.common.base_exception import DomainValidationError
  

from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed,InvalidEntityInput
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject, UnauthorizedAction

class UpdatePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self, post_id: int, data: dict, user_id: int) -> DomainPost:
        try:
            old_domain_post = self.post_repository.get_post_by_id(post_id, user_id)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except DomainValidationError as e:
            raise InvalidObject(message=e.message)
        
        try:
            old_domain_post.update_content(data.get("content", old_domain_post.content), user_id)
        except DomainValidationError as e:
            raise UnauthorizedAction(message=e.message)
        
        try:
            return self.post_repository.update_post(old_domain_post)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        