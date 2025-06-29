from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository

class DeleteComment:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository
    def execute(self, comment: DomainComment) -> None:
        return self.comment_repository.delete_comment(comment)