from threads.domain.repository import PostRepository
from threads.domain.entities import Post as DomainPost
from typing import Optional, List


class GetPostById:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self, post_id:int, auth_user_ud:int) -> Optional[DomainPost]:
        return self.post_repository.get_post_by_id(post_id, auth_user_ud)