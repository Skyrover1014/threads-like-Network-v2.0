from threads.domain.entities import Post as DomainPost
from threads.domain.repository import PostRepository

from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput, InvalidOperation
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject, UnauthorizedAction
class DeletePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self, user_id:int, post_id:int) -> None:
        try:
            target_domain_post = self.post_repository.get_post_by_id(post_id, user_id)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        
        try: 
            target_domain_post.verify_deletable_by(user_id)
        except DomainValidationError as e:
            raise UnauthorizedAction(message=e.message)
        
        try:
            return self.post_repository.delete_post(target_domain_post)
        except InvalidOperation as e:
            raise InvalidObject(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)