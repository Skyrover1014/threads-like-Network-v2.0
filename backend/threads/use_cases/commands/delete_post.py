from threads.domain.entities import Post as DomainPost
from threads.domain.repository import PostRepository

class DeletePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    def execute(self, post: DomainPost) -> None:
        return self.post_repository.delete_post(post)