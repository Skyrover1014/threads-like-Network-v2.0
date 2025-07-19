from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository

from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed,InvalidEntityInput
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable, InvalidObject, UnauthorizedAction

class UpdateComment:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self,user_id:int, comment_id:int, new_data:dict) -> DomainComment:

        try:
            old_domain_comment = self.comment_repository.get_comment_by_id(comment_id=comment_id, auth_user_id=user_id)
            if old_domain_comment is None:
                raise NotFound(message="找不到留言")
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        

        try:
            old_domain_comment.update_content(new_data.get("content", old_domain_comment.content), user_id)
        except DomainValidationError as e:
            raise UnauthorizedAction(message=e.message)

        try:
            return self.comment_repository.update_comment(old_domain_comment)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)