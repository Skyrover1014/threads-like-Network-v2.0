from threads.domain.repository import PostRepository
from threads.domain.entities import Comment as DomainComment
from typing import Optional, List


class GetCommentsByPostId:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self,auth_user_id:int, post_id:int, offset:int, limit:int) -> List[DomainComment]:
        return self.post_repository.get_comments_by_post_id(auth_user_id, post_id, offset, limit)