from threads.domain.repository import PostRepository
from threads.domain.entities import Post as DomainPost
from typing import List


class GetFollowingsPost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self,auth_user_id:int, following_ids:List[int], offset:int, limit:int) -> List[DomainPost]:
        return self.post_repository.get_posts_by_following_ids(auth_user_id, following_ids, offset, limit)