from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository

from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput, InvalidOperation
from threads.common.exceptions.use_case_exceptions import NotFound, ServiceUnavailable,InvalidObject, UnauthorizedAction

class DeleteComment:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    def execute(self, user_id:int, comment_id:int) -> None:
        try:
            target_domain_comment = self.comment_repository.get_comment_by_id(comment_id, user_id)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        
        try:
            target_domain_comment.verify_deletable_by(user_id)
        except DomainValidationError as e:
            raise UnauthorizedAction(message=e.message)
        
        try:
            return self.comment_repository.delete_comment(target_domain_comment)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        except InvalidOperation as e:
            raise InvalidObject(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)