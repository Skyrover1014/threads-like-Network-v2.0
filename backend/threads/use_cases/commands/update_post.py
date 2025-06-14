from threads.domain.entities import Post as DomainPost
from threads.domain.repository import PostRepository

class UpdatePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self, updated_post:DomainPost) -> DomainPost:
        return self.post_repository.update_post(updated_post)