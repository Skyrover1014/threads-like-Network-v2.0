from threads.domain.repository import CommentRepository
from threads.domain.entities import Comment as DomainComment
from typing import Optional


from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject


class GetCommentById:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self, comment_id:int, auth_user_id:int) -> Optional[DomainComment]:
        try:
            domain_comment = self.comment_repository.get_comment_by_id(comment_id, auth_user_id)
            if domain_comment is None:
                raise NotFound(message="此留言不存在或已經被刪除")
            return domain_comment
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)