from threads.domain.repository import CommentRepository
from threads.domain.entities import Comment as DomainComment
from typing import List


from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject
class GetCommentsByPostId:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self,auth_user_id:int, post_id:int, offset:int, limit:int) -> List[DomainComment]:
        try:
            return self.comment_repository.get_comments_by_post_id(auth_user_id, post_id, offset, limit)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)