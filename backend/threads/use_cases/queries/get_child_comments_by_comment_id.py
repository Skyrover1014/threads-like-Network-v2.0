from threads.domain.repository import CommentRepository
from threads.domain.entities import Comment as DomainComment

from typing import List



class GetChildCommentsByCommentId:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository

    def execute(self, auth_user_id:int, comment: DomainComment, offset:int, limit:int)  -> List[DomainComment]:
        return self.comment_repository.get_all_child_comments_by_comment_id(auth_user_id, comment, offset, limit)