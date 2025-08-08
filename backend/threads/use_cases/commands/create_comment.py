from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository

from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.use_case_exceptions import InvalidObject, NotFound, ServiceUnavailable
from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidOperation, InvalidEntityInput
from typing import Optional

class CreateComment:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self, author_id:int, content:str, parent_post_id:int, parent_comment_id:Optional[int] ) -> DomainComment:
        try:
            new_comment = DomainComment(id=None, author_id=author_id, content=content, parent_post_id=parent_post_id, parent_comment_id=parent_comment_id)
        except DomainValidationError as e:
            raise InvalidObject(message=e.message)
        except TypeError as e:
            raise InvalidObject(message=f"封裝 Comment 失敗: {str(e)}")
        
        try:
            return self.comment_repository.create_comment(new_comment)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)