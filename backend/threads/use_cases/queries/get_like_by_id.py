from threads.domain.entities import Like as DomainLike
from threads.domain.repository import LikeRepository
from typing import Literal

from threads.common.exceptions.repository_exceptions import InvalidEntityInput, EntityDoesNotExist, EntityOperationFailed
from threads.common.exceptions.use_case_exceptions import InvalidObject, NotFound, ServiceUnavailable


class GetLikeById:
    def __init__(self, like_repository: LikeRepository):
        self.like_repository = like_repository

    def execute(self, user_id:int,  content_id:int, content_type:Literal['post','comment']):

        try:
            return self.like_repository.get_like_by_id(user_id, content_id, content_type)
        except InvalidEntityInput as e:
            raise InvalidObject(message=e.message)
        except EntityDoesNotExist as e:
            raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable(message=e.message)
        