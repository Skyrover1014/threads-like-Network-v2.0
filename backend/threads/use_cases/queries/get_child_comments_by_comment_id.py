from threads.domain.repository import CommentRepository
from threads.domain.entities import Comment as DomainComment

from typing import List


from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput, InvalidOperation
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject, UnauthorizedAction


class GetChildCommentsByCommentId:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository

    def execute(self,comment_id:int, auth_user_id:int, offset:int, limit:int)  -> List[DomainComment]:

        try:
            domain_comment = self.comment_repository.get_comment_by_id(comment_id=comment_id,auth_user_id=auth_user_id)
            if domain_comment is None:
                raise NotFound(message="留言不存在")
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        
        try:
            return self.comment_repository.get_all_child_comments_by_comment_id(auth_user_id, domain_comment, offset, limit)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        