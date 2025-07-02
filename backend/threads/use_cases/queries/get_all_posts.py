from threads.domain.repository import PostRepository
from threads.domain.entities import Post as DomainPost
from typing import List


class GetAllPost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self,auth_user_id:int, offset:int, limit:int) -> List[DomainPost]:
        
        return self.post_repository.get_all_posts(auth_user_id, offset, limit)