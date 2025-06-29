from threads.domain.repository import CommentRepository
from threads.domain.entities import Comment as DomainComment
from typing import Optional, List


class GetCommentById:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self, comment_id:int, auth_user_ud:int) -> Optional[DomainComment]:
        return self.comment_repository.get_comment_by_id(comment_id, auth_user_ud)