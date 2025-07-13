from threads.domain.entities import Post as DomainPost
from threads.domain.repository import PostRepository
from threads.common.base_exception import DomainValidationError

from threads.common.exceptions.use_case_exceptions import InvalidObject, NotFound, ServiceUnavailable
from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput

class CreatePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self, author_id:int, author_name:str, content:str ) -> DomainPost:
        try:
            new_post = DomainPost(id=None, author_id=author_id, author_name=author_name, content=content)
        except DomainValidationError as e:
            raise InvalidObject(message=e.message)
        try:
            return self.post_repository.create_post(new_post)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            InvalidObject(message=e.message)