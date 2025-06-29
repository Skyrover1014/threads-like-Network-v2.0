from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository

from typing import Optional

class CreateComment:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self, author_id:int, content:str, parent_post_id:int, parent_comment_id:Optional[int] ) -> DomainComment:
        try:
            new_comment = DomainComment(id=None, author_id=author_id, content=content, parent_post_id=parent_post_id, parent_comment_id=parent_comment_id)
        except ValueError as e:
            raise
        return self.comment_repository.create_comment(new_comment)