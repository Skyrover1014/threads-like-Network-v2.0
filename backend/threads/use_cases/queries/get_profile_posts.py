from threads.domain.repository import PostRepository
from threads.domain.entities import User as DomainPost
from typing import Optional, List


class GetProfilePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self,auth_user_id:int, author_id:int, offset:int, limit:int) -> List[DomainPost]: 
        return self.post_repository.get_posts_by_author_id(auth_user_id, author_id, offset, limit)