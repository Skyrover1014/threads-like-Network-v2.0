from threads.domain.entities import Like as DomainLike
from threads.domain.repository import LikeRepository
from typing import Literal


class GetLikeById:
    def __init__(self, like_repository: LikeRepository):
        self.like_repository = like_repository

    def execute(self, user_id:int,  content_id:int, content_type:Literal['post','comment']):
        return self.like_repository.get_like_by_id(user_id, content_id, content_type)