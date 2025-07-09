from threads.domain.repository import CommentRepository
from threads.domain.entities import Comment as DomainComment
from typing import List


class GetCommentsByPostId:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self,auth_user_id:int, post_id:int, offset:int, limit:int) -> List[DomainComment]:
        return self.comment_repository.get_comments_by_post_id(auth_user_id, post_id, offset, limit)