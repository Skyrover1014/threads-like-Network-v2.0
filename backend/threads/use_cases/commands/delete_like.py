from threads.domain.entities import Like as DomainLike
from threads.domain.repository import LikeRepository
from typing import Literal

class DeleteLike:
    def __init__(self, like_repository: LikeRepository):
        self.like_repository = like_repository
    
    def execute(self, like: DomainLike) -> None:     
        return self.like_repository.delete_like(like)