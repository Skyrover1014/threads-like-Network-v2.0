from threads.domain.entities import Like as DomainLike
from threads.domain.repository import LikeRepository
from typing import Literal

class CreateLike:
    def __init__(self, like_repository: LikeRepository):
        self.like_repository = like_repository
    
    def execute(self,user_id: int, content_item_id:int, content_type:Literal['post', 'comment']) -> DomainLike:
        new_like = DomainLike(
            id=None, user_id=user_id, 
            content_item_id=content_item_id, 
            content_type=content_type)
        
        return self.like_repository.create_like(new_like)