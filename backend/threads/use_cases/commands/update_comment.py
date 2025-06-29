from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository

class UpdateComment:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    
    def execute(self, updated_comment:DomainComment) -> DomainComment:
        return self.comment_repository.update_comment(updated_comment)